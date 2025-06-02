from collections import defaultdict
from functools import wraps
from threading import Lock, Thread
from typing import Callable

class EventDoesNotExist(Exception):
    def __init__(self, event_name: str):
        super().__init__(f"Event '{event_name}' does not exist.")

class EventHanlderDoesNotExist(Exception):
    def __init__(self, event_name: str, handler: Callable):
        super().__init__(f"Handler '{handler.__name__}' for event '{event_name}' does not exist.")

class EventManager:
    __lock = Lock()

    def __init__(self):
        self.events = defaultdict(set)

    def on(self, event_name: str):
        def decorator(func: Callable):
            self.register_event(event_name, func)
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def register_event(self, event_name: str, handler: Callable):
        with self.__lock:
            self.events[event_name].add(handler)

    def unregister_event(self, event_name: str, handler: Callable):
        with self.__lock:
            if event_name in self.events:
                if handler in self.events[event_name]:
                    self.events[event_name].remove(handler)
                    if not self.events[event_name]:
                        del self.events[event_name]
                else:
                    raise EventHanlderDoesNotExist(event_name, handler)
            else:
                raise EventDoesNotExist(event_name)

    def emit(self, event_name, *args, **kwargs):
        with self.__lock:
            if event_name not in self.events:
                raise EventDoesNotExist(event_name)

            thread = kwargs.pop('thread', False)
            if thread:
                events = [
                    Thread(target=f, args=args, kwargs=kwargs) for f in self.events.get(event_name, [])
                ]
                for event in events:
                    event.start()
            else:
                if event_name in self.events:
                    for callback in self.events.get(event_name, []):
                        callback(*args, **kwargs)
