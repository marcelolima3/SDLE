import logging
import asyncio
import sys
import socket
import json

from LocalStorage import local_storage
from DHT import node
from P2P import Connection
from Menu.Menu import Menu as menu
from Menu import Menu as m_menu

# -- Global VARS --
queue = asyncio.Queue()
nickname = ""
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
        if menu.run(int(msg)):
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
    # return sys.stdin.readline().replace('\n', '')
    return nick.replace('\n', '')


# check if the number of args is valid
def check_argv():
    if len(sys.argv) < 2:
        print("Usage: python get.py <port> [<bootstrap ip> <bootstrap port>]")
        sys.exit(1)


# print all messages
def show():
    for m in messages:
        print(m['id'] + ' - ' + m['message'])


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
    info = {'ip': get_ip_address(), 'followers': [], 'vector_clock': []}
    asyncio.ensure_future(server.set(nickname, json.dumps(info)))


# follow a user. After, he can be found in the list "following"
def follow_user():
    print('User Nickname: ')
    user_id = sys.stdin.readline().replace('\n', '')
    userInfoJson = asyncio.ensure_future(server.get(user_id))
    if userInfoJson is None:
        print('That user doesn\'t exist!')
    else:
        userInfo = json.loads(userInfoJson)
        following.append({'id': user_id, 'ip': userInfo['ip']})
        userInfo['followers'].append({'id': nickname, 'ip': get_ip_address()})
        asyncio.ensure_future(server.set(user_id, json.dumps(userInfo)))


# Get user real ip
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


""" MAIN """
if __name__ == "__main__":
    check_argv()
    (server, loop) = start()

    try:
        print('Peer is running...')
        
        nickname = get_nickname()                                           # Get nickname from user 
        (messages, following) = local_storage.read_data(db_file+nickname)   # TODO rm nickname (it's necessary for to allow tests in the same host
       
        loop.add_reader(sys.stdin, handle_stdin)                            # Register handler to read STDIN
        build_user_info()                                                   # Register in DHT user info
        
        m = m_menu.build_menu(loop)
        asyncio.async(task(server, loop, nickname, m))                      # Register handler to consume the queue
        loop.run_forever()                                                  # Keeps the user online 
    except Exception:
        pass
    finally:
        print('Good Bye!')
        local_storage.save_data(messages, following, db_file+nickname)      # TODO rm nickname
        server.stop()
        loop.close()
