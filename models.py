class Machine:
    def __init__(self, index):
        self.index = index + 1
        self.time_left = 0

    def set_time(self, time_left):
        self.time_left = time_left


class Washer(Machine):
    def __str__(self):
        if self.time_left == 0:
            return f"W{self.index:2}:🟩"
        elif self.time_left <= 10:
            return f"W{self.index:2}:🟧 {self.time_left}m"
        return f"W{self.index:2}:🟥 {self.time_left}m"


class Dryer(Machine):
    def __str__(self):
        if self.time_left == 0:
            return f"D{self.index:2}:🟩"
        elif self.time_left <= 10:
            return f"D{self.index:2}:🟧 {self.time_left}m"
        return f"D{self.index:2}:🟥 {self.time_left}m"
