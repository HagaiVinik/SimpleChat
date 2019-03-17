#-------------     C L I E N T    C H A T     ----------------
#-
#- Writer: HAGAI VINIK
#- Date: 17/7/18
#- program creates a server of public chat.
#-

import sys
import socket
import time
import Tkinter
import tkMessageBox
from threading import Thread

#details of server.
HOST = '127.0.0.1'
PORT = 6070 #recive from server
PORT2 = 6080 #send to server

ADDR = (HOST, PORT) #reciver
ADDR2 = (HOST, PORT2)#sender
BUF_SIZE = 1024

class chat_client():

    def quit_chat(self):  #quitting first root, intro page
        self.root.destroy()
        self.client_socket.close()
        self.client_socket_rcv.close()

    def confirm(self):  # sending server user name
        user_name = self.name.get()
        if user_name != '':         
            self.root.destroy()
            self.client_socket.send('system-user_name:'+ str(user_name))
            requset = self.client_socket_rcv.recv(BUF_SIZE)
            if requset != 'user is in':
                tkMessageBox.showerror('ERROR: signing in',' request denied.')
                self.client_socket.close()
                self.client_socket_rcv.close()
    
            else:    
                recive = Thread(target = self.client_recive)
                recive.start()
                self.chat_page(user_name)

        else:
            tkMessageBox.showerror('error:','you didnt enter name.')

    def chat_page(self,user_name): # menu page
        
        def exit_chat():   #exiting menu
            self.client_socket.send('system-exit:'+ str(user_name))
            self.client_socket.close()
            self.client_socket_rcv.close()
            root2.destroy()
        def refresh():    # refreshing menu
            root2.destroy()
            self.chat_page(user_name)

        def update_menu():  #updating menu(automatic)
            self.client_socket.send('system-get_users:ok')
            time.sleep(0.25)
            self.client_socket.send('system-get_groups:ok')
            time.sleep(0.25)
            print 'updating..... '
            if self.count_connected_users != len(self.connected_users):
                self.count_connected_users = len(self.connected_users)
                refresh()

            if self.count_groups != len(self.user_groups):
                self.count_groups  = len(self.user_groups)
                refresh()
            root2.after(500, update_menu)
            

        self.client_socket.send('system-get_users:ok')
        time.sleep(0.25)
        #print 'connected users: ' + str(self.connected_users )
        self.client_socket.send('system-get_groups:ok')
        time.sleep(0.25)
        #print 'groups: ' + str(self.user_groups)
        self.count_connected_users = 0
        self.count_groups = 0
        
        root2 = Tkinter.Tk()    
        root2.title("hagai chat: hello " + user_name + ".")
        root2.geometry("300x500")

        if self.connected_users:
            for i in self.connected_users:        
                b = Tkinter.Button(root2, text='chat with :'+str(i),command= lambda x = i: self.conversation_page(x),width=30)
                b.pack(side=Tkinter.TOP)
                self.count_connected_users = self.count_connected_users + 1
        if self.user_groups:
            for i2 in self.user_groups:        
                b2 = Tkinter.Button(root2, text='chat with group :'+str(i2),command= lambda x = i2: self.conversation_page(x),width=30)
                b2.pack(side=Tkinter.TOP)
                self.count_groups = self.count_groups + 1
        if not self.user_groups and not self.connected_users:
            Tkinter.Label(root2, text="no connected users currently!").pack(side=Tkinter.TOP)
            

        
        e = Tkinter.Button(root2, text = 'new group chat ', command = lambda : self.new_group() , width = 25)
        c = Tkinter.Button(root2, text = 'exit', command = lambda : exit_chat(), width = 25)
        d = Tkinter.Button(root2, text = 'refresh', command = lambda : refresh(), width = 25)
        c.pack(side=Tkinter.BOTTOM)
        d.pack(side = Tkinter.BOTTOM)
        e.pack(side=Tkinter.BOTTOM)
        root2.protocol('WM_DELETE_WINDOW', exit_chat)

        root2.after(500, update_menu)
        root2.mainloop()
            
    def new_group(self):   #new group

        def send_new_group():    #send server details
            if entry_field1.get() == '':
                tkMessageBox.showerror('error:','please enter group name.')
            elif entry_field2.get() == '':
                tkMessageBox.showerror('error:','please enter members name.')    
            elif entry_field1.get() != '' and entry_field2.get != '':
                self.client_socket.send('system-create_group_name:'+ entry_field1.get() +':' + entry_field2.get())
                print 'sent to server:' + entry_field1.get() +': ' + entry_field2.get()
                root4.destroy()

        def exit_new_group():   #cancel
            root4.destroy()

        root4 = Tkinter.Tk()
        root4.title("hagai chat: " + self.name.get())
        root4.geometry("400x400")
        label1 = Tkinter.Label(root4 ,text = "enter name of group:").pack(side = Tkinter.TOP)
        entry_field1 = Tkinter.Entry(root4, width = 20)
        entry_field1.pack(side = Tkinter.TOP)    
        label2 = Tkinter.Label(root4 , text = "enter name of members(a,b,c):").pack(side = Tkinter.TOP)
    
        entry_field2 = Tkinter.Entry(root4 , width = 20)
        entry_field2.pack(side = Tkinter.TOP)
        but = Tkinter.Button(root4, text = "create room", command = lambda : send_new_group() , width = 40)
        but.pack(side = Tkinter.TOP)
        but2 = Tkinter.Button(root4, text = "exit", command = lambda : exit_new_group() , width = 40)
        but2.pack(side = Tkinter.TOP)
        l1 = Tkinter.Label(root4 ,text = "users: " + str(self.connected_users)).pack(side = Tkinter.TOP)
    

    def conversation_page(self,x):  #chat page, x is name of the who you chat with
        def send_message():   #sending message

            if send_to_name in self.connected_users:
                self.client_socket.send('system-send_to_user_name:'+ send_to_name +':' + entry_field.get())
                msg_list.insert(Tkinter.END, ('me: '+entry_field.get()))
                print '[sent to server-]' +'system-send_to_user_name:'+send_to_name+':'+ entry_field.get()
            elif send_to_name in self.user_groups:
                self.client_socket.send('system-send_to_group_name:'+ send_to_name +':' + entry_field.get())
                msg_list.insert(Tkinter.END, ('me: '+entry_field.get()))
                print '[sent to server-]' +'system-send_to_user_name:'+send_to_name+':'+ entry_field.get()
            msg_list.update()       
            my_msg.set("")
            entry_field.delete(0,Tkinter.END)

        def update1():  #update listbox automatic
            
            if send_to_name in self.connected_users :
                if send_to_name in self.private_messages:
                    messages = self.private_messages[send_to_name].split('\n')
                    del(self.private_messages[send_to_name])
                    for message in messages:
                        print  send_to_name + ': '+ message
                        msg_list.insert(Tkinter.END, str(send_to_name+ ': '+ message))

            elif send_to_name in self.user_groups :
                if send_to_name in self.group_messages:
                    messages = self.group_messages[send_to_name].split('\n')
                    del(self.group_messages[send_to_name])
                    for message in messages:
                        msg_list.insert(Tkinter.END, str(send_to_name+ ': '+ message))
                        print  send_to_name  + ': '+ message

            msg_list.update()
            root3.after(200, update1)
                

        send_to_name = x
        print 'chatting with: ' + send_to_name
        root3 = Tkinter.Tk()
        root3.title("hagai chat: " + self.name.get())
        root3.geometry("500x600")
        messages_frame = Tkinter.Frame(root3)
        my_msg = Tkinter.StringVar()  # For the messages to be sent.
    
        scrollbar = Tkinter.Scrollbar(messages_frame)
        msg_list = Tkinter.Listbox(messages_frame, height=20, width=70, yscrollcommand=scrollbar.set)
        scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        msg_list.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH)
        msg_list.pack()
        msg_list.insert(Tkinter.END, ('you are chatting with '+str(send_to_name)+':'))
        messages_frame.pack()    
        entry_field = Tkinter.Entry(root3, textvariable= my_msg, width = 50)
        entry_field.pack()
        send_button = Tkinter.Button(root3, text="Send", command= lambda : Thread(target = send_message()).start(), width = 50)        
        send_button.pack(side=Tkinter.TOP)
        c = Tkinter.Button(root3, text = 'exit', command = lambda : root3.destroy(), width = 50 )
        c.pack(side=Tkinter.TOP)
        root3.after(500, update1)
    
        root3.mainloop()

    def __init__(self):  #initialize, starting server, binding and connect.
        self.client_socket_rcv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket_rcv.connect(ADDR)
        self.client_socket.connect(ADDR2)

        self.connected_users = []   #list of connected users to start chat with them.  example ['Roee','Hagai']
        self.user_groups = []       #list of user groups. 
        self.private_messages = {}  #dictionary - history of messages-  name of user : messages    . example- 'hi'/whatsup?/me:ok how are you?/good thanks/'
        
        self.group_messages = {}    #dictionary - history of messages-  name of group : messages   . example- 'Roee-hi everybody/Elad-good and you?/'

        self.root = Tkinter.Tk()
        self.root.title("hagai chat")
        self.root.geometry("300x300")
        self.name = Tkinter.StringVar()  # The contents of the text box [name = me]
        self.d = Tkinter.Entry(self.root, textvariable= self.name)  # creates a textbox
        Tkinter.Label(self.root, text="enter your name please:").pack(side=Tkinter.TOP)
        self.d.pack(side=Tkinter.TOP)
        self.b = Tkinter.Button(self.root, text='sign in', fg='blue', command=self.confirm, compound="bottom")
        self.b.pack(side=Tkinter.TOP)
        self.b.config(width="50", height="50")  # config the size of the button
        Tkinter.Button(self.root, text="Quit", command=self.quit_chat).pack(side=Tkinter.BOTTOM)
        self.root.mainloop()
        
    def client_recive(self):   #reciving messages
        flag = True
        while flag == True:
            
           # print 'calling recv...'
            try:
                self.data = self.client_socket_rcv.recv(BUF_SIZE)
            except socket.error:
                flag = False
                print 'CONNECTION ERROR: server does not respond!'
                self.client_socket.close()
                self.client_socket_rcv.close()
                return
            if not self.data :
                print 'no data'
                flag = False
                
         #   print 'server say : ' + self.data
            if self.data.split(':')[0] == 'list of connected users':             
                users_str = self.data.split(':')[1]
                self.connected_users = users_str.split(',')
                del(self.connected_users[-1])
                #print ' list of users : ' + str(self.connected_users)

            if self.data.split(':')[0] == 'list of group':
                group_str = self.data.split(':')[1]
                self.user_groups = group_str.split(',')
                del(self.user_groups[-1])
                #print ' list of groups : ' + str(self.user_groups)

            if self.data.split(':')[0] == 'message from':
                self.sender_name = self.data.split(':')[1]
                if self.sender_name in self.private_messages:
                    text = str(self.private_messages[self.sender_name])
                    text = text + '\n' + str(self.data.split(':')[2])
                    self.private_messages[self.sender_name] = text
                else:
                    text = self.data.split(':')[2]
                    self.private_messages[self.sender_name] = text
                print 'message saved: [' +  self.private_messages[self.sender_name]  + ']'                  

            if self.data.split(':')[0] == 'message to group':
                self.group_name = self.data.split(':')[1]
                if self.group_name in self.group_messages:
                    text = str(self.group_messages[self.group_name])
                    text = text + '\n' + str(self.data.split(':')[2])
                    self.group_messages[self.group_name] = text
                else:
                    text = self.data.split(':')[2]
                    self.group_messages[self.group_name] = text              
                print 'message saved: ['+ self.group_messages[self.group_name] +']'
            


        
if __name__ == '__main__':    #calling prog
    chat_client()




    
