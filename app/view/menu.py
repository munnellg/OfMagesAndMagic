class MenuItem:
    def __init__(self, label):
        self.label = label

    def click(self):
        return

class BooleanMenuItem(MenuItem):
    def __init__(self, label, value=false):
        self.value = value
        self.label = label

    def click(self):
        self.value = not self.value
