# coding: utf-8

import os
import socket
import time
import urllib2

SERVER_ADDRESS = (HOST, PORT)  = '', 8888
BACKLOG = 5

def handle_request(client_connection):
 req = client_connection.recv(1024)
 http_res = b"""\
HTTP/1.1 200 OK

HELLO
"""
 client_connection.sendall(http_res)
 # time.sleep(60)


# 主进程不关闭client_socket的情况： 文件描述符耗尽
def serve_forever():
 listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 listen_socket.bind(SERVER_ADDRESS)
 listen_socket.listen(BACKLOG)

 print('Serving HTTP on port {port}'.format(port=PORT))

 clients = []
 while True:
   client_socket, client_address = listen_socket.accept()
   # clients.append(client_socket)       # Python垃圾回收机制，会在每个程序运行块结束的时候判断引用指针，如果没有引用了就会自动close掉（释放）
   if os.fork() == 0:
     listen_socket.close()
     handle_request(client_socket)
     # time.sleep(1)
     # print('child process: '+str(client_socket.fileno()))
     # client_socket.close()
     os._exit(0)
   else:
     print('test')
     print(client_socket.fileno())
     # client_socket.close()


if __name__ == '__main__':
 serve_forever()

