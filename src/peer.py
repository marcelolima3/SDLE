import logging
import asyncio
import sys
import socket
import json
from threading import Thread
import threading
import random

#from Menu.MenuFunctionalities import build_menu, get_nickname, follow_user, show_timeline, send_msg, exit_loop
#from async_tasks import task, task_follow, task_send_msg, get_followers_p2p
from LocalStorage import local_storage
from DHT import node
from P2P.Connection import Connection
from Menu.Menu import Menu
from Menu.Item import Item
import async_tasks

# -- Global VARS --
queue = asyncio.Queue()
p2p_port = ""
nickname = ""
ip_address = ""
messages = []
following = []
db_file = 'db'

# handler process IO request
def handle_stdin():
    data = sys.stdin.readline()
    asyncio.async(queue.put(data)) # Queue.put is a coroutine, so you can't call it directly.


# build the Menu
def build_menu():
    menu = Menu('Menu')
    menu.add_item(Item('1 - Show timeline', show_timeline))
    menu.add_item(Item('2 - Follow username', follow_user))
    menu.add_item(Item('3 - Send message', send_msg))
    menu.add_item(Item('0 - Exit', exit_loop))
    return menu


# get the nickname
def get_nickname():
    nick = input('Nickname: ')
    return nick.replace('\n', '')


# follow a user. After, he can be found in the list "following"
def follow_user():
    user = input('User Nickname: ')
    user_id = user.replace('\n', '')
    asyncio.async(async_tasks.task_follow(user_id, nickname, server, following, ip_address, p2p_port))
    return False


# show own timeline
def show_timeline():
    for m in messages:
        print(m['id'] + ' - ' + m['message'])
    return False


# send message to the followers
def send_msg():
    msg = input('Insert message: ')
    msg = msg.replace('\n','')
    print(msg)
    asyncio.async(async_tasks.task_send_msg(msg, server, nickname))
    return False

# exit app
def exit_loop():
    return True


# start peer or not as Bootstrap
def start():
    if len(sys.argv) > 3:
        return node.start_node(int(sys.argv[1]), sys.argv[3], int(sys.argv[4]))
    else:
        return node.start_node(int(sys.argv[1]))


# check if the number of args is valid
def check_argv():
    if len(sys.argv) < 3:
        print("Usage: python get.py <port_dht> <port_p2p> [<bootstrap ip> <bootstrap port>]")
        sys.exit(1)


# get timeline to the followings TODO
async def get_timeline():
    for user in following:
        result = await server.get(user['id'])
        userInfo = json.loads(result)
        random_follower = get_random_updated_follower(userInfo)
        if random_follower is not None:
            ask_for_timeline(random_follower, user['id'])


# temos de implementar o XOR
async def get_random_updated_follower(userInfo):
    user_followers = userInfo['followers']
    while(user_followers):
        random_follower = random.choice(user_followers.keys())
        random_follower_con = userInfo['followers'][random_follower]
        info = random_follower_con.split()
        if userInfo['vector_clock'][random_follower] > userInfo['vector_clock'][nickname] and isOnline(info[0], int(info[1])):
            return random_follower_con
        user_followers.pop(random_follower)
    return None


# check if a node is online
def isOnline(userIP, userPort):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(userIP, userPort)
    if result == 0:
        return True
    else:
        return False


# send a message to a node asking for a specific timeline
def ask_for_timeline(userIp, TLUser):
    print('TODO')


# merge all timelines TODO
def merge_timelines():
    print('TODO')


# check a set of vector clocks TODO
def check_vector_clocks():
    print('TODO')


# build a json with user info and put it in the DHT
def build_user_info():
    info = {'ip': ip_address, 'port': p2p_port, 'followers': {}, 'vector_clock': []}
    asyncio.ensure_future(server.set(nickname, json.dumps(info)))


# Get user real ip
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def start_p2p_listenner(port, stop_event):
    connection = Connection(get_ip_address(), port)
    connection.bind()
    connection.listen(stop_event)


""" MAIN """
if __name__ == "__main__":
    check_argv()
    p2p_port = sys.argv[2]
    pill2kill = threading.Event()
    thread = Thread(target = start_p2p_listenner, args = ( int(p2p_port), pill2kill, ))
    (server, loop) = start()
    try:
        print('Peer is running...')
        nickname = get_nickname()                                           # Get nickname from user
        thread.start()
        ip_address = get_ip_address()                                       # Get ip address from user
        (messages, following) = local_storage.read_data(db_file+nickname)   # TODO rm nickname (it's necessary for to allow tests in the same host

        loop.add_reader(sys.stdin, handle_stdin)                            # Register handler to read STDIN
        build_user_info()                                                   # Register in DHT user info

        m = build_menu()
        asyncio.async(async_tasks.task(server, loop, nickname, m, queue))   # Register handler to consume the queue
        loop.run_forever()                                                  # Keeps the user online
    except Exception:
        pass
    finally:
        print('Good Bye!')
        local_storage.save_data(messages, following, db_file+nickname)      # TODO rm nickname
        pill2kill.set()                                                     # Stop the thread with P2P Connection
        server.stop()                                                       # Stop the server with DHT Kademlia
        loop.close()                                                        # Stop the async loop
