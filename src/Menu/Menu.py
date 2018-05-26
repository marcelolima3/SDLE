from Menu.Item import Item

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

    def run(self, option):
        if not option > len(self.items) - 1: 
            return self.items[option-1].execute()


def show_timeline_example():
    print('timeline')
    return False


def follow_example():
    msg = input('Insert username: ')
    print(msg)
    return False


def send_msg_example():
    msg = input('Insert message: ')
    print(msg)
    return False 


def exit_loop():
    print('exit loop')
    return True


def build_menu(loop):
    menu = Menu('Menu')
    menu.add_item(Item('1 - Show timeline', show_timeline_example))
    menu.add_item(Item('2 - Follow username', follow_example))
    menu.add_item(Item('3 - Send message', send_msg_example))
    menu.add_item(Item('0 - Exit', exit_loop))
    return menu
