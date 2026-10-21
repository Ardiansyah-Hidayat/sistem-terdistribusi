import paramiko

NODES = ['192.168.56.102', '192.168.56.103', '192.168.56.104']
for ip in NODES:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port=22, username='vboxuser', password='12345')
    
    # Add to .bashrc and /etc/environment
    cmd = """grep -qxF 'export PATH="$HOME/bin:$PATH"' ~/.bashrc 2>/dev/null || echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc"""
    ssh.exec_command(cmd)
    
    # Also link to /usr/bin/ using sudo so non-interactive shells can run them
    link_cmd = "echo 12345 | sudo -S ln -sf /home/vboxuser/bin/* /usr/bin/"
    ssh.exec_command(link_cmd)
    
    ssh.close()
    print(f"Path configured for {ip}")
