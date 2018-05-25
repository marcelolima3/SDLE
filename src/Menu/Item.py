class Item:
    def __init__(self, name, function):
        self.name = name
        self.function = function
        #self.args = args lets keep this way for now

    def execute(self):
        if self.function:
            self.function()

    def draw(self):
        print("    " + self.name)