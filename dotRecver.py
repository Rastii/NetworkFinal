#!/usr/bin/env python
import struct
import socket
import hashlib


def check_hash(message,message_hash):
  h = hashlib.md5()
  h.update(message)
  if h.hexdigest() == message_hash:
    return True
  return False

def extract_message_contents(message):
  return (struct.unpack(">H", message[0:2])[0], 
          message[2:34], 
          message[34:])

def send_ack(addr, sock, seq_num, is_valid_hash):
  if is_valid_hash is True:
    sock.sendto(seq_num + struct.pack(">B", 0),addr)
  else:
    sock.sendto(seq_num + struct.pack(">B", 1),addr)

def main():
    
    mysock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    mysock.bind(('127.0.0.1', 31337))

    while True:
        data, addr = mysock.recvfrom(5000)
        seq_num, msg_hash, message = extract_message_contents(data)
        print "SEQ_NUM: %d" % seq_num
        print message
        is_valid_hash = check_hash(message, msg_hash)
        seq_num = struct.pack(">H", seq_num+1)
        send_ack(addr, mysock, seq_num, is_valid_hash)
        #data = data[0:2]
        #print data
        #data = struct.pack(">H", data)
        #print addr
        #mysock.sendto(data, (addr[0], addr[1])) 

if __name__ == "__main__":
    main()
