import random

class FadeIn:
    def __init__(self, target, start=0, end=255, time=3000):
        self.start_value = start
        self.end_value = end

        self.time = time
        self.elapsed = 0
        self.value = 0
        self.slope = float(self.end_value)/self.time

        self.target = target

    def finished(self):
        return self.elapsed >= self.time

    def animate(self, delta_t):
        self.elapsed += delta_t
        completion = min(self.elapsed, self.time)/float(self.time)
        self.value = self.start_value + self.end_value*completion
        self.target(self.value)

    def skip(self):
        self.elapsed = self.time
        self.value = self.end_value
        self.target(self.value)

class FadeOut:
    def __init__(self, target, start=255, end=0, time=3000):
        self.start_value = start
        self.end_value = end

        self.time = time
        self.elapsed = 0
        self.value = start

        self.target = target

    def finished(self):
        return self.elapsed >= self.time

    def animate(self, delta_t):
        self.elapsed += delta_t
        completion = min(self.elapsed, self.time)/float(self.time)
        self.value = self.start_value - self.start_value*completion
        self.target(self.value)

    def skip(self):
        self.elapsed = self.time
        self.value = self.end_value
        self.target(self.value)

class Delay:
    def __init__(self, time=150):
        self.time = time
        self.elapsed = 0

    def finished(self):
        return self.elapsed >= self.time

    def animate(self, delta_t):
        self.elapsed += delta_t

    def skip(self):
        self.elapsed = self.time

class FrameAnimate:
    def __init__(self, target, frames):
        self.target = target
        self.elapsed = 0
        self.frames = frames
        self.frame  = self.frames[0]
        self.trigger = self.compute_trigger_time( self.frame[1], self.frame[2] )

    def compute_trigger_time(self, normal, fuzz):
        return normal + random.uniform(0, 1)*fuzz - 1*(random.randint(0,1))

    def animate(self, delta_t):
        self.elapsed += delta_t

        if self.elapsed > self.trigger:
            r = sum(c[1] for c in self.frame[3])
            r = random.uniform(0, r)
            upto = 0
            for choice in self.frame[3]:
                if upto + choice[1] >= r:
                    self.frame = self.frames[choice[0]]
                    self.target(self.frame[0])
                    break
                upto += choice[1]

            self.elapsed = 0
            self.trigger = self.compute_trigger_time(self.frame[1], self.frame[2])

class ChooseRandom:
    def __init__(self, target, options, time=150, fuzz=0):
        self.time = time
        self.fuzz = fuzz
        self.elapsed = 0

        self.target = target
        self.trigger = self.compute_trigger_time(self.time, self.fuzz)
        self.range = sum(c[1] for c in options)
        self.options = options

    def compute_trigger_time(self, normal, fuzz):
        return abs(normal + random.uniform(0, 1)*fuzz - 1*(random.randint(0,1)))

    def animate(self, delta_t):
        self.elapsed += delta_t
        if self.elapsed > self.trigger:
            r = random.uniform(0, self.range)
            upto = 0
            for choice in self.options:
                if upto + choice[1] >= r:
                    self.target(choice[0])
                    break
                upto += choice[1]
            self.elapsed = 0
            self.trigger = self.compute_trigger_time(self.time, self.fuzz)

class Timeout:
    def __init__(self, target, args=[], time=150):
        self.time = time
        self.elapsed = time
        self.args = args
        self.target = target

    def animate(self, delta_t):
        self.elapsed += delta_t
        if self.elapsed >= self.time:
            self.elapsed = 0
            self.target(*self.args)
