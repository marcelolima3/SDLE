import asyncio, json
from P2P.Connection import Connection

# process all messages into the Queue
@asyncio.coroutine
def task(server, loop, nickname, menu, queue):
    menu.draw()
    while True:
        msg = yield from queue.get()
        if not msg == '\n' and menu.run(int(msg)):
            break
        menu.draw()
    loop.call_soon_threadsafe(loop.stop)


async def task_follow(user_id, nickname, server, following, ip_address, p2p_port):
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
            following.append({'id': user_id, 'ip': userInfo['ip']}) # é preciso guardar a porta dos que eu sigo? 
            userInfo['followers'][nickname] = f'{ip_address} {p2p_port}'
            print(f"{user_id} ----> {userInfo['followers'][nickname]}")
            asyncio.ensure_future(server.set(user_id, json.dumps(userInfo)))


# get followers port's
async def get_followers_p2p(server, nickname):
    connection_info = []
    result = await server.get(nickname)

    if result is None:
        print('ERROR - Why don\'t I belong to the DHT?')
    else: 
        userInfo = json.loads(result)
        print(userInfo)
        for user, info in userInfo['followers'].items():
            print(info)
            connection_info.append(info)
    return connection_info


async def task_send_msg(msg, server, nickname):
    connection_info = await get_followers_p2p(server, nickname)
    print('CONNECTION INFO (Ip, Port)')
    for follower in connection_info:
        print(follower)
        info = follower.split()
        send_p2p_msg(info[0], int(info[1]), msg)            


def send_p2p_msg(ip, port, message):
    connection = Connection(ip, port)  
    connection.connect()
    connection.send(message)