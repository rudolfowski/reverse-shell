import socket
from uuid import uuid4
from abc import ABC, abstractmethod
from threading import Lock
import errno
from base64 import b64decode,b64encode

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
    def __init__(self, sheller, conn, addr):
        self.id = uuid4()
        self.conn = conn
        self.addr = addr
        self.args = sheller.args
        self.console = sheller.console
        self.sheller = sheller
        self.closed = False
        self.decoder = SimpleDecoder()

    def authenticate(self):
        if not self.args.secret:
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
        if data != self.args.secret:
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

    def close(self):
        if not self.closed:
            self.closed = True
            self.conn.close()
            self.sheller.remove_implant(self)
            self.console.write(f"[+] Implant { self.addr } disconnected.")

    def send(self, data):
        if self.closed:
            return

        try:
            self.conn.send(self.decoder.encode(data))
        except Exception as e:
            self.console.write(f"[!] Error: {e}")
            self.close()

class ImplantsList:
    def __init__(self):
        self._list = []
        self._lock = Lock()
    
    def append(self, item):
        with self._lock:
            self._list.append(item)

    def extend(self, items):
        with self._lock:
            self._list.extend(items)

    def pop(self):
        with self._lock:
            return self._list.pop()

    def remove(self, item):
        with self._lock:
            self._list.remove(item)

    def __getitem__(self, index):
        with self._lock:
            return self._list[index]

    def __len__(self):
        with self._lock:
            return len(self._list)

    def __iter__(self):
        with self._lock:
            return iter(list(self._list))
