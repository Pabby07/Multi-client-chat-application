#Gagan Deep Pabby
#1001679177

#CITATIONS
#https://github.com/mikegpl/pychat
#https://www.geeksforgeeks.org/simple-chat-room-using-python/

import socket
import time
import select
import queue
from gui import *

ENCODING = 'utf-8'
HOST = 'localhost'
PORT = 1542


class Client(threading.Thread):
    def __init__(self, host, port):
        super().__init__(daemon=True, target=self.run)

        self.host = host
        self.port = port
        self.sock = None
        # Calls the function connect to a server 
        self.connected = self.connect_to_server()
        # The buffer size is set to 1024 and we expect no msg will increase this size
        self.buffer_size = 1024
        # The Queue module provides a FIFO implementation suitable for multi-threaded programming. It can be used to pass messages or other data between producer and consumer threads safely.
        self.queue = queue.Queue()
        # Locks are used in order to avoid collision(simultaneous access of objects) 
        self.lock = threading.RLock()

        self.login = ''
        self.target = ''
        self.login_list = []
        self.count=1

        if self.connected:
            # Once the connection is set up fire the Gui of the client
            self.gui = GUI(self)
            self.start()
            self.gui.start()
            # Only gui is non-daemon thread, therefore after closing gui app will quit

    def connect_to_server(self):
        """Connect to server via socket interface, return (is_connected)"""
        try:
            # Indicate that our socket will send stream of data
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connects the client to the server using the same IP and Port number as used by the server
            self.sock.connect((str(self.host), int(self.port)))
        except ConnectionRefusedError:
            # If the server is not active then the client code exits safely
            print("Server is inactive, unable to connect")
            return False
        return True

    def run(self):
        # Handles communication between client and the server using select
        inputs = [self.sock]
        outputs = [self.sock]
        while inputs:
            try:
                # The select statement monitors the socket until they become readable or writable, or a communication error occurs.
                read, write, exceptional = select.select(inputs, outputs, inputs)
            
            except ValueError:
                # If server is not on or not listening for incoming connection request we close the socket
                print('Server error')
                GUI.display_alert('Server error has occurred. Exit app')
                self.sock.close()
                break

            # If the read vaiable is not empty that means it got something from the select statement we know that we are recieving data
            if self.sock in read:
                with self.lock:
                    try:
                        # Store the data in a variable
                        data = self.sock.recv(self.buffer_size)
                    # Check if the select statement is returning error that means the client is shut down so close the socket
                    except socket.error:
                        print("Socket error")
                        # Calss the display function of the GUI and displays an alert
                        GUI.display_alert('Socket error has occurred. Exit app')
                        self.sock.close()
                        break
                # if everything runs without error then start processing the data by calling process_received_data function
                self.process_received_data(data)

            # If the write vaiable is not empty that means it got something from the select statement we know that we are ready to write data and send it
            if self.sock in write:
                if not self.queue.empty():
                    data = self.queue.get()
                    self.send_message(data)
                    self.queue.task_done()
                else:
                    time.sleep(0.05)
            # Write returns an error, in that case we close the socket
            if self.sock in exceptional:
                print('Server error')
                GUI.display_alert('Server error has occurred. Exit app')
                self.sock.close()
                break

    def process_received_data(self, data):
        # Process the data recieved from the server
        if data:
            # Decodes the data stream recieved
            message = data.decode(ENCODING)
            # Split the message by new line character
            message = message.split('\n')
            
            for msg in message:
                # If we are not recieving an empty message
                if msg != '':
                    # Split the data using ';' because the message sent by the server is created like this
                    msg = msg.split(';')

                    if msg[0] == 'msg':
                        text = msg[1] + ' >> ' + msg[3] + '\n'
                        print(msg)
                        self.gui.display_message(text)

                        # if chosen login is already in use
                        if msg[2] != self.login and msg[2] != 'ALL':
                            self.login = msg[2]

                    elif msg[0] == 'login':
                        # Updates the logged in user list for each client
                        self.gui.main_window.update_login_list(msg[1:])
        else:
            if(self.count == 1):
                # In case the user is trying to use a username that is already in use then we close the socket
                self.gui.display_message_same("Same username socket is closed")
                self.count+=1
            

    def notify_server(self, action, action_type):
        """Notify server if action is performed by client"""
        self.queue.put(action)
        if action_type == "login":
            self.login = action.decode(ENCODING).split(';')[1]
        elif action_type == "logout":
            self.sock.close()

    def send_message(self, data):
        """"Send encoded message to server"""
        with self.lock:
            try:
                self.sock.send(data)
            except socket.error:
                self.sock.close()
                GUI.display_alert('Server error has occurred. Exit app')


# Create new client with (IP, port)
if __name__ == '__main__':
    Client(HOST, PORT)
