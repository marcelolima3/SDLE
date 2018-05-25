from Item import Item 
import os 

class Menu:
    def __init__(self, name, items=None):
        self.name = name
        self.items = items or []

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def draw(self):
        print('_______________ ' + self.name + ' _______________')
        print()
        for item in self.items:
            item.draw()
        print('____________________________________')

    def run(self):
        self.draw()
        while True:
            option = int(input('> '))
            if option is 0 or option > len(self.items) - 1: 
                break
            else:
                self.items[option-1].execute()
                self.draw()

def show_timeline_example():
    print('timeline')

def follow_example():
    msg = input('Insert username: ')
    print(msg)

def send_msg_example():
    msg = input('Insert message: ')
    print(msg)    

if __name__ == "__main__":
    menu = Menu('Menu')
    menu.add_item(Item('1 - Show timeline', show_timeline_example))
    menu.add_item(Item('2 - Follow username', follow_example))
    menu.add_item(Item('3 - Send message', send_msg_example))
    menu.add_item(Item('0 - Exit', ''))
    menu.run()      