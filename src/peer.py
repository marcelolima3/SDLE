import logging
import asyncio
import sys
import socket
import json

from LocalStorage import local_storage
from DHT import node
from P2P import Connection
from Menu.Menu import Menu
from Menu.Item import Item

# -- Global VARS --
queue = asyncio.Queue()
nickname = ""
ip_address = ""
messages = []
following = []
db_file = 'db'

# handler process IO request
def handle_stdin():
    data = sys.stdin.readline()
    asyncio.async(queue.put(data)) # Queue.put is a coroutine, so you can't call it directly.


# process all messages into the Queue
@asyncio.coroutine
def task(server, loop, nickname, menu):
    menu.draw()
    while True:
        msg = yield from queue.get()
        if not msg == '\n' and menu.run(int(msg)):
            break
        menu.draw()
    loop.call_soon_threadsafe(loop.stop)


# start peer or not as Bootstrap
def start():
    if len(sys.argv) > 2:
        return node.start_node(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
    else:
        return node.start_node(int(sys.argv[1]))


# get the nickname
def get_nickname():
    nick = input('Nickname: ')
    return nick.replace('\n', '')


# check if the number of args is valid
def check_argv():
    if len(sys.argv) < 2:
        print("Usage: python get.py <port> [<bootstrap ip> <bootstrap port>]")
        sys.exit(1)    


# get timeline to the followings TODO
def get_timeline():
    print('TODO')


# merge all timelines TODO
def merge_timelines():
    print('TODO')


# check a set of vector clocks TODO
def check_vector_clocks():
    print('TODO')


# build a json with user info and put it in the DHT
def build_user_info():
    info = {'ip': ip_address, 'followers': {}, 'vector_clock': []}
    asyncio.ensure_future(server.set(nickname, json.dumps(info)))


# @asyncio.coroutine
async def task_follow(user_id):
    #task = asyncio.ensure_future(server.get(user_id))
    #result = yield from asyncio.gather(task)
    result = await server.get(user_id)
    
    if result is None:
        print('That user doesn\'t exist!')
    else: 
        userInfo = json.loads(result)
        print(userInfo)
        try:
            if userInfo['followers'][nickname]:
                print('You\'re following him!')
        except Exception:
            print('Following ' + user_id)
            following.append({'id': user_id, 'ip': userInfo['ip']})
            userInfo['followers'][nickname] = ip_address
            asyncio.ensure_future(server.set(user_id, json.dumps(userInfo)))


# follow a user. After, he can be found in the list "following"
def follow_user():
    user = input('User Nickname: ')
    user_id = user.replace('\n', '')
    asyncio.async(task_follow(user_id))

    return False


# Get user real ip
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def show_timeline():
    for m in messages:
        print(m['id'] + ' - ' + m['message'])
    return False    


# send message to the followers
def send_msg():
    msg = input('Insert message: ')
    print(msg)
    return False 


# exit app 
def exit_loop():
    return True


# build the Menu
def build_menu():
    menu = Menu('Menu')
    menu.add_item(Item('1 - Show timeline', show_timeline))
    menu.add_item(Item('2 - Follow username', follow_user))
    menu.add_item(Item('3 - Send message', send_msg))
    menu.add_item(Item('0 - Exit', exit_loop))
    return menu


""" MAIN """
if __name__ == "__main__":
    check_argv()
    (server, loop) = start()
    try:
        print('Peer is running...')
        nickname = get_nickname()                                           # Get nickname from user 
        ip_address = get_ip_address()                                       # Get ip address from user
        (messages, following) = local_storage.read_data(db_file+nickname)   # TODO rm nickname (it's necessary for to allow tests in the same host
       
        loop.add_reader(sys.stdin, handle_stdin)                            # Register handler to read STDIN
        build_user_info()                                                   # Register in DHT user info
        
        m = build_menu()
        asyncio.async(task(server, loop, nickname, m))                      # Register handler to consume the queue
        loop.run_forever()                                                  # Keeps the user online 
    except Exception:
        pass
    finally:
        print('Good Bye!')
        local_storage.save_data(messages, following, db_file+nickname)      # TODO rm nickname
        server.stop()
        loop.close()
