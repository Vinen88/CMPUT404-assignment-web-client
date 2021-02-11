#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split('\n')[0].split()[1])

    def get_headers(self,data):
        return data.split('\n\r\n')[0]

    def get_body(self, data):
        return data.split('\n\r\n')[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    def send_get(self, path, netloc):
        if path == '':
            path = '/'
        self.sendall('GET %s HTTP/1.1\r\n'%path)
        self.sendall('Host: %s\r\n'%netloc)
        self.sendall('User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0\r\n')
        self.sendall('Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n')
        self.sendall('Accept-Language: en-US,en;q=0.5\r\n')
        self.sendall('Accept-Encoding: gzip, deflate, br\r\n')
        self.sendall('Connection: Close\r\n')
        self.sendall('Upgrade-Insecure-Requests: 1\r\n')
        #self.sendall('DNT: 1\r\n') #what does this even do?
        self.sendall('\r\n') #this is important =D

    def GET(self, url, args=None):
        url_bits = urlparse(url)
        if url_bits.port == None:
            port = 80
        else:
            port = url_bits.port
        self.connect(url_bits.hostname, port) #dunno?
        self.send_get(url_bits.path, url_bits.netloc)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        print(response)
        #print(code,'\n'+body)
        self.close()
        return HTTPResponse(code, body)

    def format_content(self, content):
        formated = ''
        for key in content.keys():
            formated = formated+key+'='+content[key]+'&'
        return formated[:-1]

    def send_post_header(self, path, netloc, length): #is netloc best option here?
        self.sendall('POST %s HTTP/1.1\r\n'%path)
        self.sendall('Host: %s\r\n'%netloc)
        self.sendall('User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0\r\n')
        self.sendall('Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n')
        self.sendall('Accept-Language: en-US,en;q=0.5\r\n')
        self.sendall('Accept-Encoding: gzip, deflate, br\r\n')
        self.sendall('Content-Type: application/x-www-form-urlencoded\r\n')
        self.sendall('Content-Length: %s\r\n'%length) #hmmmm
        self.sendall('Connection: Close\r\n')
        self.sendall('Upgrade-Insecure-Requests: 1\r\n')
        #self.sendall('DNT: 1\r\n') #what does this even do?
        self.sendall('\r\n')

    def POST(self, url, args=None):
        url_bits = urlparse(url)
        if url_bits.port == None:
            port = 80
        else:
            port = url_bits.port
        if args != None:
            print(args)
            content = self.format_content(args) #this needs to be formatted
            length = len(content)
        else:    
            length = 0
        self.connect(url_bits.hostname, port)
        self.send_post_header(url_bits.path, url_bits.netloc, length)
        if args != None:
            self.sendall(content)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
