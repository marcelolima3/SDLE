import socket, sys, threading, json, asyncio

class Connection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True


    # bind an address
    def bind(self):
        server_address = (self.host, self.port)
        self.sock.bind(server_address)


    # create a connection
    def connect(self):
        server_address = (self.host, self.port)
        self.sock.connect(server_address)


    # put the socket in "Listen" mode
    def listen(self, timeline, server, nickname):
        self.sock.listen(1)

        #while not stop_event:
        while self.running:
            print('waiting for a connection')
            connection, client_address = self.sock.accept()
            manager = threading.Thread(target=process_request, args=(connection, client_address, timeline, server, nickname))
            manager.start()


    def stop(self):
        self.running = False
        socket.socket(socket.AF_INET, 
                  socket.SOCK_STREAM).connect((self.host, self.port))
        self.sock.close()


    # send a message to the other peer
    def send(self, msg, timeline=None):
        try:
            self.sock.sendall(msg.encode('utf-8'))

            data = self.sock.recv(256)
            print ('received "%s"' % data.decode('utf-8'))
            if not data.decode('utf-8') == 'ACK':
                info = json.loads(data)
                if info['type'] == 'timeline':
                    record_messages(data, timeline)
        finally:
            print('closing socket')
            self.sock.close()


# process the request, i.e., read the msg from socket (Thread)
def process_request(connection, client_address, timeline, server, nickname):
    try:
        print('connection from', client_address)
        while True:
            data = connection.recv(1024)
            if data:
                print('received "%s"' % data.decode('utf-8'))
                result = process_message(data, timeline, server, nickname)
                connection.sendall(result)
            else:
                break
    finally:
        connection.close()


def process_message(data, timeline, server, nickname):
    info = json.loads(data)
    if info['type'] == 'simple':
        timeline.append({'id': info['id'], 'message': info['msg']})
        #asyncio.async(update_vector_clock(server, 1, nickname))
        return 'ACK'.encode('utf-8')
    elif info['type'] == 'timeline':
        list = get_messages(info['id'], timeline)
        print(list)
        print(json.dumps(list))
        di = {'type': 'timeline', 'list': json.dumps(list)}
        #asyncio.async(update_vector_clock(server, len(list), nickname))
        res = json.dumps(di)
        return res.encode('utf-8')
    

async def update_vector_clock(server, n, nickname):
    result = await server.get(nickname)
    print('hei')
    userInfo = json.loads(result)
    if userInfo['vector_clock'][nickname]:
        userInfo['vector_clock'][nickname] += n
    else:
        userInfo['vector_clock'][nickname] = n
    
    asyncio.ensure_future(server.set(nickname, json.dumps(userInfo)))


def get_messages(id, timeline):
    list = []
    for m in timeline:
        if m['id'] is id:
            list.append(m)
    return list


def record_messages(data, timeline):
    info = json.loads(data)
    list = json.loads(info['list'])
    for m in list:
        timeline.append({'id': m['id'], 'message': m['message']})