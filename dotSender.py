#!/usr/bin/env python
import socket
import hashlib
import sys
from struct import pack,unpack

T_DELAY = 5
T_OFFLINE = 20
PORT = 31337

def get_arguments():
    if len(sys.argv) != 3:
      print "Usage: ./%s [ip] [file]"
      exit(1)
    return (sys.argv[1], sys.argv[2])

def get_textfile_blocks(text_file):
  try:
    with open(text_file, 'r') as f:
      data = f.read()
      blocks, remainder = divmod(len(data), 5000)
      return [data[x*5000:(x+1)*5000] for x in xrange(blocks)] \
             + [data[(blocks*5000):]]
  except:
    print "Invalid file specifi1ed -- unable to open file"


def init_socket(t_delay):
  sock = socket.socket(socket.AF_INET,
                       socket.SOCK_DGRAM)
  sock.settimeout(t_delay)
  return sock

def hash_message(message):
  h = hashlib.md5()
  h.update(message)
  return h.hexdigest()

def send_message(socket, dst_ip, dst_port, message, seq_num):
  msg_hash = hash_message(message)
  message = pack(">H", seq_num) + msg_hash + message
  socket.sendto(message, (dst_ip,dst_port))

#Seq_num should be the send_message seq_num + 1
def recv_ack(sock, seq_num):
  global T_DELAY
  global T_OFFLINE

  counter = 5
  while True:
    try:
      data,addr = sock.recvfrom(5000)
      if data is not None: 
        counter = 5
      if unpack(">H", data[0:2])[0] == seq_num:
        return True
      else:
        return False
    except socket.timeout:
      if counter >= T_OFFLINE:
        print "Tried polling the receiver for %d seconds" % T_OFFLINE
        print "The receiver is not online"
        exit(1)
      counter += T_DELAY

def main():
  global T_DELAY
  global T_OFFLINE
  global PORT

  ip_addr, text_file = get_arguments()
  data = get_textfile_blocks(text_file)
  socket = init_socket(T_DELAY)
  for x in xrange(len(data)):
    send_message(socket, ip_addr, PORT, data[x], x)
    while recv_ack(socket, x+1) is not True:
      send_message(socket, ip_addr, PORT, data[x], x)
  print "Sent %s successfully" % text_file

if __name__ == "__main__":
    main()
