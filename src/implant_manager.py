from threading import Lock
from .implant import Implant
from .event_manager import EventManager

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

class ImplantManager:
    def __init__(self, event_manager: EventManager):
        self.__implants = ImplantsList()
        self.__current = None
        self.__event_manager = event_manager

    def __len__(self):
        return len(self.__implants)

    def __iter__(self):
        return iter(self.__implants)
    
    def __getitem__(self, index):
        return self.__implants[index]

    def add_implant(self, implant):
        self.__implants.append(implant)

    def remove_implant(self, implant):
        implant.close()

        if implant in self.__implants:
            self.__implants.remove(implant)

    @property
    def current(self)-> Implant | None:
        if not self.__current:
            return None

        return self.__current

    def get_implant(self, index):
        if index < 0 or index >= len(self.__implants):
            return None
        return self.__implants[index]

    def select_implant(self, index):
        implant = self.get_implant(index)
        if implant:
            self.__current = implant
            return implant
        return None

    def set_current(self, implant):
        self.__current = implant
    
    def clear_current(self):
        self.__current = None
