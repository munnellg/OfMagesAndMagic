class FadeIn:
    def __init__(self, target, time=3000):
        self.start_opacity = 0
        self.end_opacity = 255

        self.time = time
        self.elapsed = 0
        self.opacity = 0
        self.slope = float(self.end_opacity)/self.time

        self.target = target

    def finished(self):
        return self.elapsed >= self.time

    def animate(self, delta_t):
        self.elapsed += delta_t
        self.opacity = min(int(self.elapsed * self.slope), self.end_opacity)
        self.target.set_alpha(self.opacity)

    def skip(self):
        self.elapsed = self.time
        self.opacity = self.end_opacity
        self.target.set_alpha(self.opacity)

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
