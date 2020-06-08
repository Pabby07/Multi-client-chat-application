#Gagan Deep Pabby
#1001679177

#CITATIONS
#https://github.com/mikegpl/pychat
#https://www.geeksforgeeks.org/simple-chat-room-using-python/

import socket
import threading
import queue
import time
import select

ENCODING = 'utf-8'
HOST = 'localhost'
PORT = 1542


class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__(daemon=True, target=self.listen)

        self.host = host
        self.port = port
        self.buffer_size = 2048
        # This line of code helps in reusing the port used
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.message_queues = {}
        self.connection_list = []
        self.login_list = {}
        self.lock = threading.RLock()

        # The socket is created here and if it is not able to bind the port and ip it shuts down
        self.shutdown = False
        try:
            # We bind the ip address and the port number to the socket in use
            self.sock.bind((str(self.host), int(self.port)))
            # Server starts listening and if overwhealmed then will maintain a queue of only 10
            self.sock.listen(10)
            # In non-blocking mode, if a recv() call doesn’t find any data, or if a send() call can’t immediately dispose of the data, an error exception is raised
            self.sock.setblocking(False)
            # A new thread is started
            self.start()
        except socket.error:
            # Error handling
            self.shutdown = True

        # Main loop if the there was no error
        while not self.shutdown:
            message = input()
            if message == 'quit':
                # Gives a user option to write quit to close its connection
                for sock in self.connection_list:
                    sock.close()
                self.shutdown = True
                self.sock.close()

    def listen(self):
        # Once run the server will start listening for any incoming connection
        print('Initiated listener thread')
        while True:

            with self.lock:
                try:
                    # If the client tries to connect the connection is accepted here
                    connection, address = self.sock.accept()
                except socket.error:
                    # Else sleep
                    time.sleep(0.05)
                    continue

            connection.setblocking(False)

            # Here we are maintaining a unique list of connections and append the current IP only if its a new one
            if connection not in self.connection_list:
                self.connection_list.append(connection)

            self.message_queues[connection] = queue.Queue()
            # Start a new Client thread
            ClientThread(self, connection, address)

    def update_login_list(self):
        # This part of the code takes care of updating and telling every user that the logged in user list has changed
        logins = 'login'
        for login in self.login_list:
            logins += ';' + login

        # The list also needs an All choice button if the user wants to broadcast a msg
        logins += ';ALL' + '\n'
        logins = logins.encode(ENCODING)
        for connection, connection_queue in self.message_queues.items():
            connection_queue.put(logins)


class ClientThread(threading.Thread):
    def __init__(self, master, sock, address):
        super().__init__(daemon=True, target=self.run)
        self.master = master
        self.socket = sock
        self.address = address
        # We have taken a random buffer size of 2048, that means message length cannot be greater than this
        self.buffer_size = 2048
        self.login = ''
        self.inputs = []
        self.outputs = []
        # Starts a new thread for a client
        self.start()

    def run(self):
        # This is the main menthod were starting a client thread is really implemented
        print('New thread started for connection from ' + str(self.address))

        self.inputs = [self.socket]
        self.outputs = [self.socket]
        while self.inputs:
            try:
                # The select statement monitors the socket until they become readable or writable, or a communication error occurs.
                read, write, exceptional = select.select(self.inputs, self.outputs, self.inputs)
            except select.error:
                # if any error occurs remove the connection
                self.remove_connection()
                break

            if self.socket in read:
                # If the read part is not empty that means a client is sending data
                try:
                    # Recieve data and store it
                    data = self.socket.recv(self.buffer_size)
                except socket.error:
                    # If error occurs that means that the connection was lost so we remove the connection
                    self.remove_connection()
                    break

                shutdown = self.process_data(data)

                # Empty result in socket ready to be read from == closed connection
                if shutdown:
                    self.remove_connection()
                    break

            # If the write part is not empty that means write data
            if self.socket in write:
                # The Queue module provides a FIFO implementation suitable for multi-threaded programming. It can be used to pass messages or other data between producer and consumer threads safely.
                if not self.master.message_queues[self.socket].empty():
                    data = self.master.message_queues[self.socket].get()
                    try:
                        # Send data via socket
                        self.socket.send(data)
                    except socket.error:
                        self.remove_connection()
                        break

            if self.socket in exceptional:
                self.remove_connection()

        # If exited from main run loop
        print('Closing client thread, connection' + str(self.address))

    def process_data(self, data):
        """Process data received by client's socket"""
        shutdown = False
        if data:
            # Decode data and split it using ';' in 3 parts because the message is created in such a way from the client
            message = data.decode(ENCODING)
            message = message.split(';', 3)

            if message[0] == 'login':
                tmp_login = message[1]
                if(message[1] in self.master.login_list):
                    shutdown=True
                    return shutdown


                if tmp_login != message[1]:
                    prompt = 'msg;server;' + message[1] + ';Login ' + tmp_login \
                             + ' already in use. Your login changed to ' + message[1] + '\n'
                    self.master.message_queues[self.socket].put(prompt.encode(ENCODING))

                self.login = message[1]
                self.master.login_list[message[1]] = self.socket
                print(message[1] + ' has logged in')

                # Update list of active users, send it to all the clients
                self.master.update_login_list()

            # If the user quits using any method then server prints logout
            elif message[0] == 'logout':
                print(message[1] + ' has logged out')
                shutdown = True

            # If the broadcast option is not selected then we send the data only to the intended user
            elif message[0] == 'msg' and message[2] != 'ALL':
                msg = data.decode(ENCODING) + '\n'
                data = msg.encode(ENCODING)
                target = self.master.login_list[message[2]]
                self.master.message_queues[target].put(data)

            elif message[0] == 'msg':
                msg = data.decode(ENCODING) + '\n'
                data = msg.encode(ENCODING)
                for connection, connection_queue in self.master.message_queues.items():
                    if connection != self.socket:
                        connection_queue.put(data)
        else:
            shutdown = True
        return shutdown

    def remove_connection(self):
        # If the user quits aggressively by closing the UI ir types quit or tries to close the connection is any way this part of teh code handles it
        print('Client {} has disconnected.'.format(self.login))
        if self.login in self.master.login_list:
            # Remove the user from the login_list so all the user can know that client has left
            del self.master.login_list[self.login]
        if self.socket in self.master.connection_list:
            # Romove its information that was stored to send and recieve data
            self.master.connection_list.remove(self.socket)
        if self.socket in self.master.message_queues:
            del self.master.message_queues[self.socket]
        self.socket.close()
        # Finally update the logged in list for all the users
        self.master.update_login_list()


# Create new server with (IP, port)
if __name__ == '__main__':
    server = Server(HOST, PORT)
