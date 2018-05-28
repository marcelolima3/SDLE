import socket
import sys
import threading

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
    def listen(self, stop_event):
        self.sock.listen(1)

        while not stop_event:
            print('waiting for a connection')
            connection, client_address = self.sock.accept()
            manager = threading.Thread(target=self.__process_request, args=(connection, client_address,))
            manager.start()


    # process the request, i.e., read the msg from socket (Thread)
    def __process_request(self, connection, client_address):
        try:
            print('connection from', client_address)
            while True:
                data = connection.recv(128)
                if data:
                    print('received "%s"' % data.decode('utf-8'))
                    connection.sendall('ACK'.encode('utf-8'))
                else:
                    print('no more data from', client_address)
                    break
        finally:
            connection.close()
   
    
    # send a message to the other peer
    def send(self, msg):
        try:
            self.sock.sendall(msg.encode('utf-8'))
           
            data = self.sock.recv(16)
            print ('received "%s"' % data.decode('utf-8'))
        finally:
            print('closing socket')
            self.sock.close()