from .receiver import Receiver
from .sender   import Sender
import queue

q = queue.PriorityQueue()
recv = Receiver()
send = Sender()
recv.run(q)
send.run(q)