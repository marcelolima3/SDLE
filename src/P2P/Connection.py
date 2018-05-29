import socket, sys, threading, json, asyncio

class Connection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # bind an address
    def bind(self):
        server_address = (self.host, self.port)
        self.sock.bind(server_address)


    # create a connection
    def connect(self):
        server_address = (self.host, self.port)
        self.sock.connect(server_address)


    # put the socket in "Listen" mode
    def listen(self, timeline):
        self.sock.listen(1)

        #while not stop_event:
        while True:
            print('waiting for a connection')
            connection, client_address = self.sock.accept()
            manager = threading.Thread(target=process_request, args=(connection, client_address, timeline))
            manager.start()


    # send a message to the other peer
    def send(self, msg):
        try:
            self.sock.sendall(msg.encode('utf-8'))

            data = self.sock.recv(16)
            print ('received "%s"' % data.decode('utf-8'))
        finally:
            print('closing socket')
            self.sock.close()


# process the request, i.e., read the msg from socket (Thread)
def process_request(connection, client_address, timeline):
    try:
        print('connection from', client_address)
        while True:
            data = connection.recv(1024)
            if data:
                print('received "%s"' % data.decode('utf-8'))
                result = process_message(data, timeline)
                connection.sendall(result)
            else:
                break
    finally:
        connection.close()


def process_message( data, timeline):
    info = json.loads(data)
    if info['type'] == 'simple':
        timeline.append({'id': info['id'], 'message': info['msg']})
        return 'ACK'.encode('utf-8')
    elif info['type'] == 'timeline':
        list = get_messages(info['id'], timeline)
        return json.loads(list)
    

def get_messages(id, timeline):
    list = []
    for m in timeline:
        if m['id'] is id:
            list.append(m)
    return list
