import chatgpt_wrapper
import sys, time

sys.stdout.reconfigure(write_through=True)

class ChatGPTLLM:
    def __init__(self):
        self.reset = True
        self.bot = chatgpt_wrapper.ChatGPT()
        self._head = ""

    def session(self):
        self.bot.new_conversation()
        self.reset = True
        return None
        
    def head(self, text):
        if self.reset:
            self._head += text
        return None
        
    def generate(self, text, times, stop, max_tokens=500):
        times.append(time.time())
        if self.bot is None:
            self.session()
        
        if self.reset:
            text = self._head + text
            self._head = ""
            self.reset = False
        response = self.bot.ask(text)
        times.append(time.time())
        return response

    def stateful(self):
        return True

model = ChatGPTLLM()


import socket
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 9876))
s.listen(5)

while True:
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established!")
    request = ""
    def read():
        return clientsocket.recv(1024).decode('utf-8').split("\n")
    loop = True
    while loop:
        lines = read()
        for line in lines:
            if line == "---":
                loop = False
                break
            print("`%s`"%line)
            request += line
    data = json.loads(request)
    print(data)
    result = getattr(model, data["method"])(*data["args"])
    clientsocket.send(("%s\n---\n"%json.dumps(result)).encode('utf-8'))
    print("done")
    clientsocket.close()