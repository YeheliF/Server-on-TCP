import socket
import sys
import os 

TCP_PORT = int(sys.argv[1])
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', TCP_PORT))
s.listen()
while True:
    conn, addr = s.accept()
    conn.settimeout(1.0)
    path_name = " "
    flag = 0;
    i = 0
    while True:
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data: break
            line = data.decode().splitlines()
            
            #going over each line to check if address/ connection type
            for l in line:
                print (l)
                words = l.rsplit(" ")
                
                #if there are more than two word - we will check
                if len(words) >= 2:
                    
                    # i is a flag for the beigning of the html from user
                    if i == 0:
                        path_name = words[1]
                        
                        # this is special request - mean the user want index.html
                        if path_name == "/":
                            path_name = "files/index.html"
                            
                        # this is special request - mean the user want result.html
                        elif path_name == "/redirect":
                            
                            # set special flag value
                            flag = 2
                        else:
                            path_name = "files" + path_name
                    if words[0] == "Connection:":
                        if flag != 2 and words[1] == "close":
                            flag = 1
                i += 1
            
            #if we finished reading input of html
            if line[len(line) - 1] == "":
                connect = " "
                if flag == 1:
                    connect = "Connection: close"
                else:
                    connect = "Connection: keep-alive"
                    
                # special flag for redirecting page
                if flag == 2:
                    message = "HTTP/1.1 301 Moved Permanently\nConnection: close\nLocation: /result.html\n\n"
                    flag = 1
                    conn.send(message.encode())
                path_no_file = path_name.rsplit("/", 1)
                
                #check if file exisits
                if os.path.isfile(path_name):
                    script_dir = os.path.dirname(__file__)
                    abs_file_path = os.path.join(script_dir, path_name)
                    
                    # read .jpg and .ico as binary
                    if path_name.find(".jpg") != -1 or path_name.find(".ico") != -1:
                        file_name = open(abs_file_path, "rb")
                        file_stats = os.stat(abs_file_path)
                        length = file_stats.st_size
                        message = "HTTP/1.1 200 OK\n" + connect + "\nContent length:" + str(length) + "\n\n" 
                        new_message = message.encode() + file_name.read()
                        conn.send(new_message)
                        file_name.close()
                    
                    #read other types of files
                    else:
                        file_name = open(abs_file_path, "r")
                        file_stats = os.stat(abs_file_path)
                        length = file_stats.st_size
                        message = "HTTP/1.1 200 OK\n" + connect + "\nContent length:" + str(length) + "\n\n" + file_name.read()
                        conn.send(message.encode())
                        file_name.close()
                        
                #if there is no file - return error
                else:
                    message = "HTTP/1.1 404 Not Found\n Connection: close\n\n"
                    conn.send(message.encode())
                    
                    #set flag do we close connection
                    flag = 1
                
                # flag = 1 - means connection needs to close 
                if flag == 1:
                    conn.close()
                    break
                else:
                    i = 0
                    continue
        #if there is timeout - no exception - close connection 
        except socket.timeout:
            conn.close()
            pass
            break

