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
import urllib.parse
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
        # data is the response
        # data_str = data.decode('utf-8')
        code = int(data.split('\r\n')[0].split(" ")[1])  # status code
        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        # data_str = data.decode('utf-8')
        body = data.split('\r\n\r\n')[1]  # body
        print("body: ",body) # print body
        return body
    
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
        code = 500
        body = ""
        
        # check correct http
        if not url.startswith("http:"):
            print("cannot handle https")
            quit()

        # Parse the URL
        parsed_url = urlparse(url)
        
        # Extract the port number
        port = parsed_url.port
        host = parsed_url.hostname
        path = parsed_url.path

        if not port:
            port = 80
        if not path:
            path = "/"
 
        request = b"GET "+path.encode()+b" HTTP/1.1\nHost: "+host.encode()+b" Connection: close\n\n"  # request
        request_str = f"GET {path} HTTP/1.1\r\n"\
                    f"Host: {host}\r\n"\
                    f"Connection: close\r\n\r\n"

        try: 
            self.connect(host,port)
            self.sendall(request_str)
            response= self.recvall(self.socket)  # string
            self.close()
            code =self.get_code(response)
            body = self.get_body(response)
        except:
            code = 404

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        if not url.startswith("http:"):
            print("cannot handle https")
            quit()

        # Parse the URL
        parsed_url = urlparse(url)
        # Extract the port number
        port = parsed_url.port
        host = parsed_url.hostname
        path = parsed_url.path

        if args:
            encoded_args = urllib.parse.urlencode(args)
        else:
            encoded_args = ""

        request = f"POST {path} HTTP/1.1\r\n"\
                    f"Host: {host}\r\n"\
                    f"Content-Type: application/x-www-form-urlencoded\r\n"\
                    f"Content-Length: {len(encoded_args)}\r\n"\
                    f"Connection: close\r\n"\
                    f"\r\n"\
                    f"{encoded_args}"

        try:
            self.connect(host,port)   # connect the host and port
            self.sendall(request)
            # s.shutdown(socket.SHUT_WR)
            response = self.recvall(self.socket)
            self.close()

            code = self.get_code(response)
            body = self.get_body(response)
        except:
            code = 404
        
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
