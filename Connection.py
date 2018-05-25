import socket
import sys

class Connection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind(self):
        server_address = (self.host, self.port)
        print('starting up on %s port %s' % server_address)
        self.sock.bind(server_address)

    def connect(self):
        server_address = (self.host, self.port)
        print('starting up on %s port %s' % server_address)
        self.sock.connect(server_address)

    def start(self):
        self.sock.listen(1)

        while True:
            # Wait for a connection
            print('waiting for a connection')
            connection, client_address = self.sock.accept()
            try:
                print('connection from', client_address)

                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(128)
                    print('received "%s"' % data)
                    if data:
                        print('sending data back to the client')
                        connection.sendall(data)
                    else:
                        print('no more data from', client_address)
                        break
            finally:
                # Clean up the connection
                connection.close()

    def start2(self):
        try:
            # Send data
            message = 'This is the message.  It will be repeated.'
            print ('sending "%s"' % message)
            self.sock.sendall(message.encode('utf-8'))

            # Look for the response
            amount_received = 0
            amount_expected = len(message)
            
            while amount_received < amount_expected:
                data = self.sock.recv(128)
                amount_received += len(data)
                print ('received "%s"' % data)

        finally:
            print('closing socket')
            self.sock.close()