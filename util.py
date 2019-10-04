import time


class Animator:
    def __init__(self, delay=0.1, max_states=5, once=False):
        self.max_states = max_states
        self.delay = delay
        self.state = 0
        self.once = once
        self.done = False
        self.last_time = time.monotonic()

    def __call__(self):
        if self.last_time + self.delay < time.monotonic():
            self.last_time = time.monotonic()
            self.state += 1
            if self.state >= self.max_states:
                if self.once:
                    self.done = True
                else:
                    self.state = 0
        return self.state
