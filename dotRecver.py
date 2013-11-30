#!/usr/bin/env python
import struct
import socket
import hashlib

MAX_UINT = 0xffffffff

def check_hash(message,message_hash):
  h = hashlib.md5()
  h.update(message)
  if h.hexdigest() == message_hash:
    return True
  return False

def extract_message_contents(message):
  return (struct.unpack("!I", message[0:4])[0], 
          message[4:20], 
          message[20:])

def send_ack(addr, sock, seq_num, is_valid_hash):
  if is_valid_hash is True:
    sock.sendto(seq_num + struct.pack("!B", 0),addr)
  else:
    sock.sendto(seq_num + struct.pack("!B", 1),addr)

def main():
    global MAX_UINT
    mysock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    mysock.bind(('127.0.0.1', 31337))

    while True:
        data, addr = mysock.recvfrom(5020)
        seq_num, msg_hash, message = extract_message_contents(data)
        print "DATA_LENGTH: ", len(data)
        print "SEQ_NUM: ", seq_num
        print "MSG_HASH: ", msg_hash.encode('hex')
        print "Message: ", message
        is_valid_hash = check_hash(message, msg_hash)
        if seq_num == MAX_UINT:
          seq_num = struct.pack("!I", 0)
          print "Received FIN, sending FIN-ACK"
        else:
          seq_num = struct.pack("!I", seq_num+1)
        send_ack(addr, mysock, seq_num, is_valid_hash)

if __name__ == "__main__":
    main()
