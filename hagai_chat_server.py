#-------------     S E R V E R    C H A T     ----------------
#-
#- Writer: HAGAI VINIK
#- Date: 10/7/18
#- program creates a server of public chat.
#-


import time
import socket
import threading

#details of server.
HOST = '127.0.0.1'
PORT = 6070  #port sending
PORT2 = 6080 #port reciving

ADDR = (HOST, PORT) #sending
ADDR2 = (HOST, PORT2) #reciving
BUF_SIZE = 2048

class AsyncClientHandler( threading.Thread ): #class inheritance from Thread, handle each client with parameters
    def __init__( self, client_socket,client_socket_rcv, chat_server ):
        threading.Thread.__init__( self )
        self.client_socket = client_socket
        self.client_socket_rcv = client_socket_rcv
        self.chat_server = chat_server
        
    def run( self ):   #run function
        print 'check: running...   ' 
        want_to_exit = False

        data = ''
        while want_to_exit == False :               # main prog: getting data in a loop(everytime) from client.
            try:
                data = self.client_socket_rcv.recv(BUF_SIZE)
            except socket.error:                
                print 'check:third %s' % self.client_socket
                print ' user disconnected'
                if user_name in self.chat_server.users: 
                    del self.chat_server.users[user_name]
                want_to_exit = True                
                return

            if not data:
                want_to_exit = True                
                try:
                    if user_name in self.chat_server.users: 
                        del self.chat_server.users[user_name]
                    return
                except UnboundLocalError:
                    pass
                print 'user disconnected'   
            print 'request: '+ data

            if data.split(':')[0] == 'system-user_name' :   #first.
                user_name = data.split(':')[1]    
                self.chat_server.users[user_name] = self.client_socket    #adding user name to users dictionary and his connection - socket.
                self.client_socket.send('user is in')

            if data.split(':')[0] == 'system-get_users' : #-- option 1 --get list of connected users.       ------ info set to user
                users_str = ''
                for user in self.chat_server.users:
                    if user != user_name :
                        users_str = users_str + str(user) + ','
                self.client_socket.send('list of connected users:'+users_str)
                print '[sent to client-] list of connected users:' + users_str

            if data.split(':')[0] == 'system-get_groups' : #-- option 2 -- get list of groups that user is in them      ------ info set to user
                group_str = ''
                for g in self.chat_server.room_list:
                    userslist = self.chat_server.room_list[g].split(',')
                    if user_name in userslist:
                        group_str = group_str + str(g) + ','
                self.client_socket.send('list of group:' +group_str)
                print '[sent to client-] list of group:' + group_str
        


            if data.split(':')[0] == 'system-send_to_user_name' : #-- option 3 -- send private message.  ------ info set to user
                message = data.split(':')[2]  #message part 
                send_to_user = data.split(':')[1]   #addressee part
                if send_to_user not in self.chat_server.users:
                    self.client_socket.send('ERROR1: user- ' +send_to_user+'was not found')
                else:
                    self.chat_server.users[send_to_user].send('message from:' + str(user_name)+':' + str(message))
                    print ' [sent to different client] ' + ' message from:' + str(user_name)+':' + str(message)


            if data.split(':')[0] == 'system-create_group_name':   # -- option 4 -- create a private group of users.
                name_of_group = data.split(':')[1]
                name_of_members = data.split(':')[2]+ ',' + user_name
                self.chat_server.room_list[name_of_group] = name_of_members
                print 'room "'+ name_of_group + '" created. [' + name_of_members + ']'


            if data.split(':')[0] == 'system-send_to_group_name' :  #--option 5 -- send a private group a message.         ------ info set to user
                message = data.split(':')[2]  #message 
                name_of_group_tosend = data.split(':')[1] #name of group to send
                
                if name_of_group_tosend not in self.chat_server.room_list:
                    self.client_socket.send('ERROR2: group not found')
                else:
                    group_users = self.chat_server.room_list[name_of_group_tosend] #str of users to send 
                    list_of_users = group_users.split(',') # list of users to senf
                    for send_to_user in list_of_users:
                        if send_to_user not in self.chat_server.users: #check first if random user is still connected
                            self.client_socket.send('ERROR3: user "' + send_to_user + '" was not found. ')
                        else:
                            if send_to_user != user_name:
                                self.chat_server.users[send_to_user].send('message to group:'+ name_of_group_tosend +':'+ str(user_name)+ ' - ' + str(message)) #message to group:killers:roee- hi everybody.
                            print '[sent to clients] ' + 'message to group:'+ name_of_group_tosend +':'+ str(user_name)+ '-' + str(message)  


            if data.split(':')[0] == 'system-exit':          # -- option 6 -- exit of chat and disconnect from server .
                want_to_exit = True                          # disconnecting from server.
                for i in self.chat_server.room_list:                     # run on all groups and clear user name from doctionary of rooms of users.
                    l1 = (self.chat_server.room_list[i]).split(',')      # list of users in random room
                    if user_name in l1: 
                        l1.remove(user_name)        # if user in list, remove him
                        for member in l1:
                            try:
                                self.chat_server.users[member].send('message to group:' +i + ':' + str(user_name) + ' left the room.')    #message for all users of group that user_name left.
                            except KeyError:
                                print 'message didnt send user "'+ str(member) + '" wasnt found.'
                        str_room_members = ','.join(l1)          #convert back to str
                        self.chat_server.room_list[i] = str_room_members     # set back the str of members in room    
                if user_name in self.chat_server.users: 
                    del self.chat_server.users[user_name]
                print "'" + user_name+ "'" + ' left the chat, messages sent.'        
        self.client_socket.close()       #disconnect from server        
        self.client_socket_rcv.close()
        print 'socket of user closed.'
class hagai_chat_server():

    def __init__(self):  #initialize server, binding,accept.
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(ADDR)
        self.server_socket.listen(5)
        self.server_socket_rcv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket_rcv.bind(ADDR2)
        self.server_socket_rcv.listen(5)
        
        print 'server is running ' , ADDR , ADDR2
        self.room_list = {}         #dictionary - name of rooms, name of members
        self.room_list['hackers'] = 'hagai,guy,gg'
        
        self.users = {}         # dictionary  -  names , connections
        self.users_rcv = {}     # another dict to recive name

        
        flag_call = True 
        while flag_call == True:
            print 'calling accept...'
            (client_socket , address) = self.server_socket.accept()  #6057 send to client
            (client_socket_rcv, address2) = self.server_socket_rcv.accept() #6055  recive from client
            if client_socket and client_socket_rcv:
                print 'client connected - ' + str(address) + ', ' + str(address2) 
                ach = AsyncClientHandler(client_socket,client_socket_rcv, self)
                ach.start()
                
            
if __name__ == '__main__':
    hagai_chat_server()

