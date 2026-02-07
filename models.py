class Machine:
    def __init__(self, index):
        self.index = index + 1
        self.time_left = 0

    def set_time(self, time_left):
        self.time_left = time_left


class Washer(Machine):
    def __str__(self):
        if self.time_left == 0:
            return f"Washer {self.index:02}: 🟩"
        elif self.time_left <= 10:
            return f"Washer {self.index:02}: 🟧 ({self.time_left} min remaining)"
        return f"Washer {self.index:02}: 🟥 ({self.time_left} min remaining)"


class Dryer(Machine):
    def __str__(self):
        if self.time_left == 0:
            return f"Dryer {self.index:02}: 🟩"
        elif self.time_left <= 10:
            return f"Dryer {self.index:02}: 🟧 ({self.time_left} min remaining)"
        return f"Dryer {self.index:02}: 🟥 ({self.time_left} min remaining)"
