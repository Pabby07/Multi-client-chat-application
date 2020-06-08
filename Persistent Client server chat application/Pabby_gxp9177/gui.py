#Gagan Deep Pabby
#1001679177

#CITATIONS
#https://github.com/mikegpl/pychat
#https://www.geeksforgeeks.org/simple-chat-room-using-python/

#importing libraries
import tkinter as tk
import threading
from tkinter import scrolledtext
from tkinter import messagebox
import time
ENCODING = 'utf-8'


class GUI(threading.Thread):
    def __init__(self, client):
        super().__init__(daemon=False, target=self.run)
        # Set a font variable that dictates the date font and size that is displayed
        self.font = ('Helvetica', 13)
        self.client = client
        self.login_window = None
        self.main_window = None
    # Whenever the start method is called it calls the run function of the the thread
    def run(self):
        # Creating the objects of different classes for further use
        self.login_window = LoginWindow(self, self.font)
        self.main_window = ChatWindow(self, self.font)
        self.notify_server(self.login_window.login, 'login')
        self.main_window.run()

    @staticmethod
    def display_alert(message):
        # Creates a alert box
        messagebox.showinfo('Error', message)

    def update_login_list(self, active_users):
        # The user log in list is updated via this logic
        self.main_window.update_login_list(active_users)

    def display_message_same(self, message):
        # Display the message sent by other user on a the chat window
        self.main_window.display_message(message)
    def display_message(self, message):
        # Display the message sent by other user on a the chat window
        self.main_window.display_message(message)

    def send_message(self, message):
        # Populates the queue
        self.client.queue.put(message)

    def set_target(self, target):
        
        self.client.target = target

    def notify_server(self, message, action):
        # Send notice to the user of any new action
        print("action ===========", action)
        print("action ===========", message)
        data = action + ";" + message
        data = data.encode(ENCODING)
        self.client.notify_server(data, action)

    def login(self, login):
        self.client.notify_server(login, 'login')

    def logout(self, logout):
        self.client.notify_server(logout, 'logout')


class Window(object):
    # Creates the window part of the GUI
    def __init__(self, title, font):
        self.root = tk.Tk()
        self.title = title
        self.root.title(title)
        self.font = font


class LoginWindow(Window):
    def __init__(self, gui, font):
        super().__init__("Login", font)
        self.gui = gui
        self.label = None
        self.entry = None
        self.button = None
        self.login = None

        self.build_window()
        self.run()

    def build_window(self):
        # Build login window and set widgets positioning and event bindings
        self.label = tk.Label(self.root, text='Enter your login', width=20, font=self.font)
        # We need to pack all the elements together
        self.label.pack(side=tk.LEFT, expand=tk.YES)

        self.entry = tk.Entry(self.root, width=20, font=self.font)
        self.entry.focus_set()
        # Tells the Gui where to place the entry
        self.entry.pack(side=tk.LEFT)
        # Finally bond everything together
        self.entry.bind('<Return>', self.get_login_event)

        self.button = tk.Button(self.root, text='Login', font=self.font)
        self.button.pack(side=tk.LEFT)
        self.button.bind('<Button-1>', self.get_login_event)

    def run(self):
        # Tkinter enters the main loop using this command and hanldes all the events
        self.root.mainloop()
        self.root.destroy()

    def get_login_event(self, event):
        #Get login from login box and close login window
        self.login = self.entry.get()
        self.root.quit()


class ChatWindow(Window):
    # Class to create the chat window where every information is displayed
    def __init__(self, gui, font):
        super().__init__("Python Chat", font)
        self.gui = gui
        self.messages_list = None
        self.logins_list = None
        self.entry = None
        self.send_button = None
        self.exit_button = None
        
        self.check_message = None
        
        self.lock = threading.RLock()
        self.target = ''
        
        self.perma_list = []
        self.unique_user_all_time_list = set()
        
        
        self.login = self.gui.login_window.login


        self.build_window()

    def build_window(self):
        # Set the position of the window
        self.root.geometry('750x500')
        self.root.minsize(600, 400)

        
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E)

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # List of messages of the GUI
        frame00 = tk.Frame(main_frame)
        frame00.grid(column=0, row=0, rowspan=2, sticky=tk.N + tk.S + tk.W + tk.E)

        # List of logins part of the GUI
        frame01 = tk.Frame(main_frame)
        frame01.grid(column=1, row=0, rowspan=3, sticky=tk.N + tk.S + tk.W + tk.E)
        
        
        
        
        
        frame07 = tk.Frame(main_frame)
        frame07.grid(column=2, row=0, rowspan=3, sticky=tk.N + tk.S + tk.W + tk.E)
        
        
        
        

        
        frame02 = tk.Frame(main_frame)
        frame02.grid(column=0, row=2, columnspan=1, sticky=tk.N + tk.S + tk.W + tk.E)

        # Buttons on the GUI
        frame03 = tk.Frame(main_frame)
        frame03.grid(column=0, row=3, columnspan=2, sticky=tk.N + tk.S + tk.W + tk.E)

        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=8)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)

        # If the message is to long we need a scroll bar
        self.messages_list = scrolledtext.ScrolledText(frame00, wrap='word', font=self.font)
        self.messages_list.insert(tk.END, 'Welcome to Python Chat\n')
        self.messages_list.configure(state='disabled')

        # Listbox widget for displaying active users and selecting them
        self.logins_list = tk.Listbox(frame01, selectmode=tk.SINGLE, font=self.font,
                                      exportselection=False)
        self.logins_list.bind('<<ListboxSelect>>', self.selected_login_event)

        
        self.perm_list = tk.Listbox(frame07, selectmode=tk.SINGLE, font=self.font,
                                      exportselection=False)
        self.perm_list.bind('<<ListboxSelect>>', self.selected_login_event)

        
        self.entry = tk.Text(frame02, font=self.font)
        self.entry.focus_set()
        self.entry.bind('<Return>', self.send_entry_event)

        # Button for sending a message also works if enter is pressed
        self.send_button = tk.Button(frame03, text='Send', font=self.font)
        self.send_button.bind('<Button-1>', self.send_entry_event)

        # Button for exiting th GUI and disconnecting from the server
        self.exit_button = tk.Button(frame03, text='Exit', font=self.font)
        self.exit_button.bind('<Button-1>', self.exit_event)
        
        #button creation and binding for the checking of messages of offline users/persistent file/asynchrnous messages 
        
        self.check_message = tk.Button(frame03, text='check', font=self.font)
        self.check_message.bind('<Button-1>', self.send_entry_event)
        
        

        
        self.messages_list.pack(fill=tk.BOTH, expand=tk.YES)
        self.logins_list.pack(fill=tk.BOTH, expand=tk.YES)
        
        
        
        self.perm_list.pack(fill=tk.BOTH, expand=tk.YES)
        
        
        
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.send_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.exit_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        
        
        
        self.check_message.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        
        
        

        # Handles if the user quits aggressively
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing_event)
        print(self.logins_list.get(0))

    def run(self):
        
        self.root.mainloop()
        self.root.destroy()

    def selected_login_event(self, event):
        # User can select a target from the list displayed and send a message
        if(self.logins_list.curselection()):
            target = self.logins_list.get(self.logins_list.curselection())
        elif(self.perm_list.curselection()):
            target = self.perm_list.get(self.perm_list.curselection())
        self.target = target
        self.gui.set_target(target)




    def send_entry_event(self, event):
        # Sends the message typed in the message box
        text = self.entry.get(1.0, tk.END)
        if text != '\n':
            # Create the message to be sent 
            
            message = 'msg;' + self.login + ';' + self.target + ';' + text[:-1]
            #print(message)
            # Calls the send message function
            self.gui.send_message(message.encode(ENCODING))
            self.entry.mark_set(tk.INSERT, 1.0)
            self.entry.delete(1.0, tk.END)
            self.entry.focus_set()
        else:
            
            #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",self.login)
            #read the persistent file of offline users line by line 
            file = open("persistent_file.txt", "r")

            list_of_file = file.readlines()
            
            
            display_list = []
            #add all the users to the list of offline users 
            for i in range(len(list_of_file)):

                test = list_of_file[i].split()

                if(test[4] == self.login):

                    display_list.append(list_of_file[i])
            file.close()
            #write to the persistent file of users 
            file = open("persistent_file.txt", "w")
            keep_list = []
            for i in range(len(list_of_file)):
                
                test = list_of_file[i].split()

                if(test[4] != self.login):
                    
                    keep_list.append(list_of_file[i])
                    
            for i in keep_list:
                 file.write(i)
            #close the file 
            file.close()
            self.messages_list.configure(state='normal')
            if(len(display_list) != 0):
                for i in display_list:
                    self.messages_list.insert(tk.END, i)
                self.messages_list.configure(state='disabled')
                self.messages_list.see(tk.END)
            else:
                self.messages_list.configure(state='normal')
                self.messages_list.insert(tk.END, "No messages to display in your Queue \n")
                self.messages_list.configure(state='disabled')
                self.messages_list.see(tk.END)
                    
            
            
            
#configuring the messages 
        with self.lock:
            self.messages_list.configure(state='normal')
            if text != '\n':
                self.messages_list.insert(tk.END, text)
            self.messages_list.configure(state='disabled')
            self.messages_list.see(tk.END)
        
        
        self.logins_list.selection_clear(0, tk.END)
        self.perm_list.selection_clear(0, tk.END)
        
        
        
        
        
        
        return 'break'

    def exit_event(self, event):
        # Notify all the users to update their list if any user left
        self.gui.notify_server(self.login, 'logout')
        self.root.quit()

    def on_closing_event(self):
        # Exit window when 'x' button is pressed
        self.exit_event(None)

    def display_message(self, message):
        
        with self.lock:
            # By default message entry is disabled, once message arrives enable th entry and display it then we again disable the entry so that it cannot be altered again
            self.messages_list.configure(state='normal')
            self.messages_list.insert(tk.END, message)
            self.messages_list.configure(state='disabled')
            self.messages_list.see(tk.END)

        # If the user name is duplicate we close the socket and close the GUI
        if(message=="Same username socket is closed"):
            time.sleep(2.5)
            self.on_closing_event()

    def update_login_list(self, active_users):
        # Update listbox with list of active users
        
        
        
        
        #display list of the active users in the username

        for i in active_users:
            
            if(i not in self.perma_list):
                self.perma_list.append(i)

        
        
        
        #display a list of logged in users 
        self.logins_list.delete(0, tk.END)
        for user in active_users:
            self.logins_list.insert(tk.END, user)
        
        
        
        self.perm_list.delete(0, tk.END)
        #open and read  a file of offline users 
        f = open("offline_users.txt", "r")
        my_list = f.readlines()
        #add all the unique users to the list which have logged in ever
       # print("@@@@@@@@@@@@@@@", my_list)
        for j in my_list:
            self.unique_user_all_time_list.add(j)
        #print("###############", self.unique_user_all_time_list)
        for user in self.unique_user_all_time_list:
            #code for unicast
            if(user != "ALL"):
                self.perm_list.insert(tk.END, user)
        
        
        
        
        
#        self.logins_list.select_set(1)
#        
#        
#        
#                
        if(self.logins_list.curselection()):                    
            self.target = self.logins_list.get(self.logins_list.curselection())






















