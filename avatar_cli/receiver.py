import socket
import time
import json
from avatar_cli.runner import Runner


class Receiver(Runner):
    def __init__(self, addr = "localhost", port = 9998):
        self.addr = addr
        self.port = port

    def loop(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((socket.gethostname(), 9998))
        self.s.listen(5)
        while True:
            try:
                cs, address = self.s.accept()
                size = int.from_bytes(cs.recv(4), 'big')
                message = ""
                while True:
                    new_msg = cs.recv(size)
                    if new_msg:
                        message += new_msg.decode('utf-8')
                        if len(message) == size:
                            break
                    else:
                        break
                try:
                    action_list = json.loads(message)
                except json.decoder.JSONDecodeError as e:
                    print(e)
                    print("---\n")
                    print(message)

                for a in action_list:
#                    print("receiver: %s"%a)
                    self.queue.put(a)
                cs.close()
            except KeyError as e:
                print(e)
