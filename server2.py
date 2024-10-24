import socket
import time
import json
import qlock_angle as qlock
import threading 

class ChatServer():
    def __init__(self, host='192.168.1.120', port=12348):
        self.host = host
        self.port = port
        
        self.bag_flag=False
        self.gelendata = ""
        self.flag= False
        self.gidendata=""
        
        self.thread = threading.Thread(target = self.start_server,)
        self.thread.start()
        
    def gelen_mesaj(self, conn):
        self.mflag=True
        while self.mflag==True:
            try:
                ldata = conn.recv(1024)
                if not ldata:
                    break
                if ldata.decode("utf-8") == 'exit':
                    print(f'Client disconnected')
                    break
                else:
                    self.flag = True
                    message = json.loads(ldata.decode())
                    self.tip = message.get("type")
                    self.gelendata = message.get("action")
                    self.deger=message.get("value")
                    print(self.gelendata+(" gelen"))
                    
                                       
            
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        print('breaklandı')
        self.mflag = False
        
        conn.close()
        self.conn_res()

    def giden_mesaj(self, conn):
        while self.mflag == True:
            try:
                
                if self.gidendata == 'exit':
                    conn.sendall(data.encode('utf-8'))
                    print("Closing connection.")
                    break
                conn.sendall(self.gidendata.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message: {e}")
                break
        conn.close()

    def start_server(self,):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(20)
            print(f"Server listening on {self.host}:{self.port}")
            self.client_socket, self.client_address = self.server_socket.accept()
            print(f"Accepted connection from {self.client_address}")

            client_handler = threading.Thread(target=self.gelen_mesaj, args=(self.client_socket,))
            client_handler.start()

            client_handler1 = threading.Thread(target=self.giden_mesaj, args=(self.client_socket,))
            client_handler1.start()

        except Exception as e:
            print(f"Error in server: {e}")
        finally:
            self.server_socket.close()

    def conn_res(self):
        self.bag_flag=True
        print("reset calıstı")
        time.sleep(3)
        
        print("bekleme")

        self.start_server()
               
