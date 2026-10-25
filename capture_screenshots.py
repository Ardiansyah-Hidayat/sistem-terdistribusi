import asyncio
import base64
import json
import os
import subprocess
import time
import urllib.request
import httpx
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE_URL = "http://127.0.0.1:8000"
OUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)


async def prepare_sample_data():
    """Ensure all 3 nodes are online and populate clean sample files for the PPT."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # Login as admin
        r = await client.post("/api/auth/login", json={"role": "admin", "username": "ardi", "password": "ardi123"})
        token = r.json()["token"]
        headers = {"X-Auth-Token": token}

        # Ensure guest access is ON and guest authority is OFF initially
        await client.post("/api/admin/guest-access", json={"enabled": True}, headers=headers)
        await client.post("/api/admin/guest-authority", json={"enabled": False}, headers=headers)

        # Ensure all 3 nodes are online
        nodes = (await client.get("/api/nodes", headers=headers)).json()
        for n in nodes:
            if n["status"] != "online":
                await client.post(f"/api/nodes/{n['id']}/toggle", headers=headers)

        # Clear existing files via API and remove any leftover untracked files on disk
        await client.delete("/api/files/all", headers=headers)
        base_storage = os.path.join(os.path.dirname(__file__), "storage_data")
        for n_dir in ["node1", "node2", "node3"]:
            p = os.path.join(base_storage, n_dir)
            if os.path.isdir(p):
                for fn in os.listdir(p):
                    fp = os.path.join(p, fn)
                    if os.path.isfile(fp):
                        try:
                            os.remove(fp)
                        except OSError:
                            pass

        # Wait for heartbeat to reflect 0 files on all nodes
        await asyncio.sleep(3.2)

        # Upload 3 realistic files for presentation
        sample_files = [
            ("Laporan_Sistem_Terdistribusi.pdf", b"%PDF-1.7\n" + b"0" * (418 * 1024), "application/pdf"),
            ("Dataset_Telemetri_Node_2026.csv", b"timestamp,node,latency_ms,status\n" * 4200, "text/csv"),
            ("Topologi_Master_Worker.png", open("diagrams/arsitektur_sistem.png", "rb").read(), "image/png"),
        ]
        for fname, content, mime in sample_files:
            await client.post("/api/upload", files={"file": (fname, content, mime)}, headers=headers)
            await asyncio.sleep(3.2)

        return token


class CDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.msg_id = 0

    async def __aenter__(self):
        self.ws = await websockets.connect(self.ws_url, max_size=50 * 1024 * 1024)
        return self

    async def __aexit__(self, *args):
        if self.ws:
            await self.ws.close()

    async def send(self, method, params=None):
        self.msg_id += 1
        target_id = self.msg_id
        payload = {"id": target_id, "method": method, "params": params or {}}
        await self.ws.send(json.dumps(payload))
        while True:
            raw = await self.ws.recv()
            data = json.loads(raw)
            if data.get("id") == target_id:
                if "error" in data:
                    raise RuntimeError(f"CDP error in {method}: {data['error']}")
                return data.get("result", {})

    async def eval_js(self, expression):
        return await self.send("Runtime.evaluate", {
            "expression": expression,
            "awaitPromise": True,
            "returnByValue": True
        })

    async def screenshot(self, filepath, height=920):
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": 1360,
            "height": height,
            "deviceScaleFactor": 2,
            "mobile": False
        })
        await asyncio.sleep(0.4)
        res = await self.send("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(res["data"]))
        print(f"[OK] Saved screenshot: {filepath}")


async def main():
    token = await prepare_sample_data()

    # Start headless Chrome with remote debugging
    user_data = os.path.join(os.environ.get("TEMP", "."), f"chrome_ss_{int(time.time())}")
    proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=9229",
        f"--user-data-dir={user_data}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1360,1150",
        f"{BASE_URL}/"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        # Wait for DevTools endpoint
        ws_url = None
        for _ in range(30):
            await asyncio.sleep(0.3)
            try:
                with urllib.request.urlopen("http://127.0.0.1:9229/json", timeout=2) as resp:
                    targets = json.loads(resp.read().decode())
                    for t in targets:
                        if t.get("type") == "page" and "webSocketDebuggerUrl" in t:
                            ws_url = t["webSocketDebuggerUrl"]
                            break
                if ws_url:
                    break
            except Exception:
                pass

        if not ws_url:
            raise RuntimeError("Could not connect to Chrome DevTools")

        async with CDPClient(ws_url) as cdp:
            await cdp.send("Page.enable")
            await cdp.send("Runtime.enable")

            # Wait for fonts and initial render
            await asyncio.sleep(2.0)

            # 1. Login Page Screenshot
            await cdp.eval_js("localStorage.clear(); initAuth();")
            await asyncio.sleep(0.8)
            await cdp.eval_js("document.getElementById('admin-user').value = 'ardi'; document.getElementById('admin-pass').value = 'ardi123';")
            await cdp.screenshot(os.path.join(OUT_DIR, "1_halaman_login.png"), height=780)

            # 2. Admin Dashboard (All 3 Nodes Active)
            await cdp.eval_js("document.getElementById('admin-form').requestSubmit();")
            await asyncio.sleep(2.0)
            await cdp.eval_js("refreshAll();")
            await asyncio.sleep(0.8)
            h_res = await cdp.eval_js("Math.max(document.documentElement.scrollHeight, document.body.scrollHeight, 1020)")
            page_h = h_res.get("result", {}).get("value", 1040)
            await cdp.screenshot(os.path.join(OUT_DIR, "2_dashboard_admin_normal.png"), height=page_h + 40)

            # 3. Node Failure Simulation & Failover State
            # Disable node1 and show failover toast
            await cdp.eval_js("document.getElementById('toast-container').innerHTML = '';")
            await cdp.eval_js("""
                (async () => {
                    const btn = document.querySelector('[data-action="toggle-node"][data-id="node1"]');
                    if (btn) btn.click();
                })();
            """)
            await asyncio.sleep(1.8)
            await cdp.eval_js("showToast('Laporan_Sistem_Terdistribusi.pdf diunduh dari node2 (Failover Aktif).', 'success');")
            await asyncio.sleep(0.4)
            h_res = await cdp.eval_js("Math.max(document.documentElement.scrollHeight, document.body.scrollHeight, 1020)")
            page_h = h_res.get("result", {}).get("value", 1040)
            await cdp.screenshot(os.path.join(OUT_DIR, "3_simulasi_node_mati_failover.png"), height=page_h + 40)

            # Restore node1 back to online
            await cdp.eval_js("""
                (async () => {
                    const btn = document.querySelector('[data-action="toggle-node"][data-id="node1"]');
                    if (btn) btn.click();
                })();
            """)
            await asyncio.sleep(1.2)

            # 4. Guest Mode View
            await cdp.eval_js("handleLogout(true);")
            await asyncio.sleep(0.8)
            await cdp.eval_js("handleGuestLogin();")
            await asyncio.sleep(2.0)
            await cdp.eval_js("document.getElementById('toast-container').innerHTML = '';")
            h_res = await cdp.eval_js("Math.max(document.documentElement.scrollHeight, document.body.scrollHeight, 920)")
            page_h = h_res.get("result", {}).get("value", 960)
            await cdp.screenshot(os.path.join(OUT_DIR, "4_tampilan_mode_tamu.png"), height=page_h + 40)

    finally:
        proc.terminate()


if __name__ == "__main__":
    asyncio.run(main())
