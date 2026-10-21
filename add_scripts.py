import paramiko

NODES = {
    '192.168.56.102': 8001,
    '192.168.56.103': 8002,
    '192.168.56.104': 8003
}

for ip, port in NODES.items():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=22, username='vboxuser', password='12345', timeout=5)
        
        stop_cmd = f"fuser -k {port}/tcp; pkill -9 -f node.main; echo 'Storage Node STOPPED!'"
        start_cmd = f"cd ~/sistem_terdistribusi && nohup python3 -m uvicorn node.main:app --host 0.0.0.0 --port {port} > ~/sistem_terdistribusi/node.log 2>&1 & echo 'Storage Node STARTED!'"
        
        ssh.exec_command(f'echo "{stop_cmd}" > ~/stop.sh && chmod +x ~/stop.sh')
        ssh.exec_command(f'echo "{start_cmd}" > ~/start.sh && chmod +x ~/start.sh')
        ssh.close()
        print(f"Scripts stop.sh and start.sh added to VM {ip}")
    except Exception as e:
        print(f"Error on {ip}: {e}")
