#!/usr/bin/env python

import socket

def main():
    
    mysock = socket.sock(socket.AF_INET, socket.SOCK_DGRAM)

    mysock.bind(('127.0.0.1', 31337))

    while True:

        data, addr = mysock.recv()

        mysock.sendto(data, (addr[0], addr[1])) 

if __name__ == "__main__":
    main()
