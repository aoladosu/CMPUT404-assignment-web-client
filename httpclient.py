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
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    
    def __init__(self):
        self.headers = [""]
    
    def get_host_port(self,url):
        # not to self check for port first
        
        # get port
        parsed = urlparse(url)
        scheme = parsed.scheme
        if (parsed.port):
                port = parsed.port
        elif (scheme == "https"):
            port = 443
        elif (scheme == "http"):
            port = 80
        elif (scheme == "ftp"):
            port = 21
        else:
            raise Exception("Couldn't find port number")
        
        # get path
        path = parsed.path if (parsed.path) else '/'

        # get host -----
        host = parsed.hostname
                
        return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        split = data.split(' ')
        try:
            code = int(split[1])
        except:
            raise Exception("Code is not a number")
        return code

    def get_headers(self, data):
        split = data.split("\r\n")
        split.pop(0)
        headers = {}
        for item in split:
            if (item):
                info = item.split(':')
                title = info[0]
                value = info[1].strip()
                headers[title] = value
                if ("Location" in info[0]):
                    info.pop(0)
                    headers[title] = ":".join(info).strip()
            else:
                break
        return headers

    def get_body(self, data):
        split = data.split("\r\n")
        split.pop(0)
        index = 0
        for item in split:
            if (not item):
                body = '\r\n'.join(split[index:])
                break
            index += 1
                
        return body
    
    def create_post(self, host, path, data):
        
        try:
            encode = urlencode(data)
            length = str(len(encode))
        except:
            encode = ''
            length = '0'
        
        br = "\r\n"
        message = "POST " + path + " HTTP/1.1" + br
        message += "Host: " + host + br
        message += "User-Agent: Mozilla" + br
        message += "Content-Type: application/x-www-form-urlencoded" + br   
        message += "Content-Length: " + length + br
        message += br
        message += encode + br
        
        #print(message)
        return message
    
    def create_get(self, host, path, referrer=''):
        
        br = "\r\n"
        message = "GET " + path + " HTTP/1.1" + br
        message += "Host: " + host + br
        message += "User-Agent: Mozilla" + br                           ######
        message += "Accept: text/html,text/css,application/x-www-form-urlencoded,*/*" + br
        message += "Accept-Language: en-US,en" + br
        message += "DNT: 1" + br
        message += "Connection: close" + br
        if referrer:
            message += "Referer: " + referrer + br
        message += br
            
        #print(message)
        return message
    
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

    def GET(self, url, args=None):
        code = 300
        headers = {}
        old_url = ''
        headers['Location'] = url
        while ((code >= 300) and (code < 400)):
            # follow redirect
            new_url = headers['Location']
            host, port, path = self.get_host_port(new_url)
            message = self.create_get(host, path, old_url)
            self.connect(host, port)
            self.sendall(message)
            data = self.recvall(self.socket)
            self.close()
            code = self.get_code(data)
            headers = self.get_headers(data)
            old_url = new_url
            
        body = self.get_body(data)
        print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        host, port, path = self.get_host_port(url)
        message = self.create_post(host, path, args)
        self.connect(host, port)
        self.sendall(message)
        data = self.recvall(self.socket)
        self.close()
        code = self.get_code(data)
        headers = self.get_headers(data)
        body = self.get_body(data)
        print(body)
        return HTTPResponse(code, body)

    def command(self, url, command="POST", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    #args = {'a':'aaaaaaaaaaaaa','b':'bbbbbbbbbbbbbbbbbbbbbb','c':'c','d':'012345\r67890\n2321321\n\r'}
    #client.command('localhost:8080', "POST", args )
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
