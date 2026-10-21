import paramiko

NODES = {
    '192.168.56.102': {'id': 'node1', 'port': 8001},
    '192.168.56.103': {'id': 'node2', 'port': 8002},
    '192.168.56.104': {'id': 'node3', 'port': 8003}
}

for ip, conf in NODES.items():
    port = conf['port']
    nid = conf['id']
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=22, username='vboxuser', password='12345', timeout=5)

        sftp = ssh.open_sftp()
        try:
            sftp.mkdir('/home/vboxuser/bin')
        except Exception:
            pass

        scripts = {
            'start': f"#!/bin/bash\ncd /home/vboxuser/sistem_terdistribusi && nohup python3 -m uvicorn node.main:app --host 0.0.0.0 --port {port} > /home/vboxuser/sistem_terdistribusi/node.log 2>&1 &\necho '🟢 Storage Node ({nid}) STARTED on port {port}!'\n",
            'stop': f"#!/bin/bash\nfuser -k {port}/tcp 2>/dev/null\npkill -9 -f node.main\necho '🔴 Storage Node ({nid}) STOPPED!'\n",
            'files': f"#!/bin/bash\necho '=== DAFTAR FILE DI {nid} ==='\nls -lh /home/vboxuser/sistem_terdistribusi/storage_data/{nid}/\n",
            'status': f"#!/bin/bash\ncurl -s --connect-timeout 1 http://localhost:{port}/health || echo '🔴 Node is OFFLINE / STOPPED'\necho ''\n",
            'logs': f"#!/bin/bash\ntail -f /home/vboxuser/sistem_terdistribusi/node.log\n",
            'menu': f"#!/bin/bash\necho '==============================='\necho '🚀 SHORTCUT COMMANDS:'\necho '   start  -> Nyalakan server node'\necho '   stop   -> Matikan server node'\necho '   status -> Cek kesehatan node'\necho '   files  -> Lihat isi file di node ini'\necho '   logs   -> Streaming live aktivitas'\necho '==============================='\n"
        }

        for name, content in scripts.items():
            remote_path = f"/home/vboxuser/bin/{name}"
            with sftp.file(remote_path, 'w') as f:
                f.write(content)
            ssh.exec_command(f"chmod +x {remote_path}")

        sftp.close()

        # Copy to /usr/local/bin using password
        ssh.exec_command("echo 12345 | sudo -S cp /home/vboxuser/bin/* /usr/local/bin/ && echo 12345 | sudo -S chmod +x /usr/local/bin/*")

        ssh.close()
        print(f"[OK] Shortcuts successfully installed on VM {ip} ({nid})")
    except Exception as e:
        print(f"[ERROR] on {ip}: {e}")
