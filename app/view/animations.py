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
