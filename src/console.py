from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import print_formatted_text

class Console:
    def __init__(self, input_callback=None, prompt="sh3ll => "):
        
        self.__session = PromptSession(prompt)
        self.__callback = input_callback
        self.__prompt = [prompt]

        self.__running = True

    def handle_input(self, callback):
        self.__callback = callback

    
    def run(self):
        with patch_stdout():
            while self.__running:
                try:
                    text = self.__session.prompt()
                    text = text.strip()
                    if text:
                        if self.__callback:
                            self.__callback(text) 
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break;
    

    def write(self, text):
        print_formatted_text(text.strip())

    def close(self):
        self.__running = False

    def set_prompt(self, prompt):
        self.__prompt.append(prompt)
        self.__update_prompt()

    def back(self):
        self.__prompt.pop()
        self.__update_prompt()

    def __update_prompt(self):
        self.__session.message = self.__prompt[-1]
        self.__session.app.invalidate()
