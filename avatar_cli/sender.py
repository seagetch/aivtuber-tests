import requests
import queue
import time
import copy
from avatar_cli.runner import Runner

import random
class EyeBlinkTask:
    def __init__(self):
        self.lastScheduled = time.time()
    def schedule(self):
        if time.time() > self.lastScheduled - 0.5:
            nextSchedule = self.lastScheduled + random.uniform(2, 3)
            self.lastScheduled = nextSchedule
            shutterSchedule = random.uniform(0.05, 0.1)
            return [
                [nextSchedule                        , nextSchedule + shutterSchedule * 0.5, { "eye_blink": 0.7 }],
                [nextSchedule + shutterSchedule * 0.5, nextSchedule + shutterSchedule      , { "eye_blink": 1.0 }],
                [nextSchedule + shutterSchedule      , nextSchedule + shutterSchedule * 1.5, { "eye_blink": 0.7 }],
                [nextSchedule + shutterSchedule * 1.5, nextSchedule + shutterSchedule * 2.0, { "eye_blink": 0.2 }]
            ]
        else:
            return []

import math
import random
class IdleSwingMotion:
    def __init__(self):
        pass
    
    def update(self):
        STEP = 4
        t = time.time() % STEP
        t = float(t) / STEP
        value = math.sin(t * math.pi * 2)
        if abs(value) > 0.8:
            t2 = (abs(value) - 0.8) / 0.2
            value2 = math.sin(t2 * math.pi / 2) * 0.1;
        else:
            value2 = 0
        value *= 0.2
        return { "body_roll": value, "head_roll": value2 if t<0.5 else -value2 }

class Sender(Runner):
    def __init__(self, addr = "localhost", port = 9999):
        self.addr = addr
        self.port = port
        self.active  = queue.PriorityQueue()
        self.waiting = queue.PriorityQueue()
        self.default_action_map = {"eye_blink": 0.2, "mouth_x": 0.0, "mouth_y": 0.01, "face_pitch": 0.5}
        self.tasks = [EyeBlinkTask()]
        self.realtime_tasks = [IdleSwingMotion()]

    def loop(self):
        while True:
            while not self.queue.empty():
                self.waiting.put(self.queue.get())
            
            for task in self.tasks:
                actions = task.schedule()
                for action in actions:
                    self.waiting.put(action)
            
            while not self.waiting.empty():
                if self.waiting.queue[0][0] <= time.time():
#                    print("sender: waiting -> active", self.waiting.queue[0])
                    self.active.put(self.waiting.get())
                else:
                    break
            while not self.active.empty():
                if self.active.queue[0][1] <= time.time():
#                    print("sender: active -> done", self.active.queue[0])
                    self.active.get()
                else:
                    break
            full_action_map = copy.copy(self.default_action_map)
            for task in self.realtime_tasks:
                full_action_map.update(task.update())
            min_end_time = None
            for action in self.active.queue:
                start_time, end_time, action_map = action
                if action_map is None:
                    continue
                full_action_map.update(action_map)
                if min_end_time is None or end_time < min_end_time:
                    min_end_time = end_time
            
            try:
                res = requests.post("http://localhost:9999/blendshapes", json=full_action_map, timeout=0.000000001)
            except Exception as e:
                pass
            time_to_left = min_end_time - time.time() if not (min_end_time is None) else 10
            if time_to_left > 0:
                time.sleep(min(time_to_left, 0.01))
