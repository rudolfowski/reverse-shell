import socket
from uuid import uuid4
from abc import ABC, abstractmethod
import errno
from base64 import b64decode,b64encode

from .event_manager import EventManager
from .console import Console

class MessageDecoder(ABC):

    @abstractmethod
    def decode(self, data):
        raise ValueError("Subclasses should implement this!")

    @abstractmethod
    def encode(self, data):
        raise ValueError("Subclasses should implement this!")

class SimpleDecoder(MessageDecoder):
    def decode(self, data):
        return data.decode()

    def encode(self, data):
        return data.encode()

class Base64Decoder(MessageDecoder):
    def decode(self, data):
        return b64decode(data).decode()

    def encode(self, data):
        return b64encode(data.encode()).decode()

class Implant:
    def __init__(self, conn, addr, args, console: Console, event_manager: EventManager):
        self.id = uuid4()
        self.conn = conn
        self.addr = addr
        self.event_manager = event_manager
        self.console = console
        self.secret = args.secret

        self.closed = False
        self.decoder = SimpleDecoder()

    def __eq__(self, other):
        return self.id == other.id

    def authenticate(self):
        if not self.secret:
            return True

        self.conn.settimeout(5)
        try:
            buffer = self.conn.recv(1024)
        except socket.timeout:
            self.console.write("[-] Implant timed out.")
            return False
        finally:
            self.conn.settimeout(None)

        if not buffer:
            self.console.write("[-] No secret key provided.")
            return False

        data = self.decoder.decode(buffer)
        if data != self.secret:
            self.console.write("[-] Invalid secret key.")
            return False

        self.console.write(f"[+] Implant authenticated {self.addr}")

        return True

    def process(self):
        while True:
            try:
                data = self.conn.recv(1024)
                if not data:
                    break

                res = self.decoder.decode(data)
                self.console.write(res)
            except OSError as e:
                # Handle the case where the socket is closed
                if e.errno == errno.EBADF:
                    break
            except Exception as e:
                self.console.write(f"[!] Error: {e}")
                break

        self.close()

    def close(self, fire_event=False):
        """Close the implant connection and clean up resources."""

        if not self.closed:
            try:
                self.conn.shutdown(socket.SHUT_RDWR)
            except OSError as e:
                if e.errno == errno.ENOTCONN:
                    # Socket is already closed
                    pass
            self.conn.close()
            self.closed = True
            if fire_event:
                self.event_manager.emit("implant_closed", self)

    def send(self, data):
        if self.closed:
            return

        try:
            self.conn.sendall(self.decoder.encode(data))
        except Exception as e:
            self.console.write(f"[!] Error: {e}")
            self.close()

