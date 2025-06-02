from .console import Console
from .implant_manager import ImplantManager
from .event_manager import EventManager

class CommandManager:
    def __init__(self,
                 console: Console, 
                 implants_manager: ImplantManager,
                 event_manager: EventManager):

        self.console = console
        self.event_manager = event_manager
        self.implants = implants_manager
        self.console.handle_input(self.__handle_input)

    def __handle_input(self, data: str):
        text = data.strip()
        system_command = False
        if not text:
            self.console.write("[-] No cmd provided")
            return

        if text.startswith("/"):
            text = text[1:]
            system_command = True

        # if no implant selected we can use only system commands 
        if not self.implants.current and not system_command:
            self.console.write("[-] No implant selected.")
            return

        if system_command:
            split = text.split(" ")
            cmd = split[0]
            args = split[1:]

            if cmd == "exit":
                self.__exit()
                return

            elif cmd == "help":
                self.__print_help()
                return

            elif cmd == "ls":
                self.__list_implants()
                return

            elif cmd.startswith("use"):
                if len(args) != 1:
                    self.console.write("[-] Usage: /use <implant_id>")
                    return
                self.__select_implant(args[0])
                return

        if self.implants.current:
            self.implants.current.handle_input(text)

    def __exit(self):
        self.event_manager.emit("close")

    def __print_help(self):
        s = """
Available commands:
    /exit - Exit the program
    /help - Show this help message
    /list - List all implants
    /use <implant_id> - Select an implant to interact with
        """
        self.console.write(s)
    
    def __list_implants(self):
        if not self.implants:
            self.console.write("[-] No implants connected.")
            return

        for i, implant in enumerate(self.implants):
            self.console.write(f"[+] Implants: {len(self.implants)}")
            self.console.write(f"[+] {i + 1}: {implant.addr[0]}:{implant.addr[1]}")

    def __select_implant(self, index):

        try:
            index = int(index)
        except ValueError:
            self.console.write(f"[-] Invalid index: {index}")
            return

        if not self.implants:
            self.console.write("[-] No implants connected.")
            return

        implant = self.implants.select_implant(index - 1)
        if implant:
            self.console.set_prompt(f"[{implant.addr}] => ")
        else:
            self.console.write(f"[-] Implant not found.")

