import logging
import asyncio
import sys

from kademlia.network import Server
from LocalStorage import local_storage

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
def task(server, loop, nickname):
    while True:
        msg = yield from queue.get()
        messages.append({
            'id' : nickname,
            'message': msg.replace('\n', '')
        })
        asyncio.ensure_future(server.set(nickname, msg)) 
        # TODO supposed to be a json file with the user info
        # build a menu with options like "tweet", "follow user", "leave"

# starting a node
def start_node(Port, BTIp="", BTPort=0): 
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # DEBUG
    log = logging.getLogger('kademlia')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    server = Server()
    server.listen(Port)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    # the first peer don't do that
    if not BTPort == 0:    
        bootstrap_node = (BTIp, int(BTPort))
        loop.run_until_complete(server.bootstrap([bootstrap_node]))

    return (server, loop)


# start peer or not as Bootstrap
def start():
    if len(sys.argv) > 2:
        return start_node(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
    else: 
        return start_node(int(sys.argv[1]))

# get the nickname
def get_nickname():
    print('Nickname: ')
    return sys.stdin.readline().replace('\n', '')


# check if the number of args is valid
def check_argv():
    if len(sys.argv) < 2:
        print("Usage: python get.py <port> [<bootstrap ip> <bootstrap port>]")
        sys.exit(1)


# print all messages
def show():
    for m in messages:
        print(m['id'] + ' - ' + m['message'])

""" MAIN """
if __name__ == "__main__":
    check_argv()
    (server, loop) = start()
    
    try:
        print('Peer is running...')
        nickname = get_nickname()
        (messages, following) = local_storage.read_data(db_file+nickname)  # TODO rm nickname (it's necessary for to allow tests in the same host)
        show()        
        
        loop.add_reader(sys.stdin, handle_stdin)
        asyncio.async(task(server, loop, nickname))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print('loop.close()')
        local_storage.save_data(messages, following, db_file+nickname)    # TODO rm nickanme
        server.stop()
        loop.close()