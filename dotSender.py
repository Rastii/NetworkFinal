#!/usr/bin/env python
import socket
import hashlib
import sys
from struct import pack,unpack

T_DELAY = 5
T_OFFLINE = 20
PORT = 31337
MAX_UINT = 0xffffffff

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
  return h.digest()

def send_message(socket, dst_ip, message, seq_num):
  global PORT
  msg_hash = hash_message(message)
  message = pack("!I", seq_num) + msg_hash + message
  socket.sendto(message, (dst_ip,PORT))

def send_fin_message(socket, dst_ip, message):
  global MAX_UINT
  global PORT
  msg_hash = hash_message(message)
  message = pack("!I", MAX_UINT) + msg_hash + message
  socket.sendto(message, (dst_ip,PORT))

def check_seq_error(expected_seq_num, data):
  seq_num = unpack("!I", data[0:4])[0]
  error = unpack("!B", data[4:5])[0]
  if error == 1:
    print "The receiver received a corrupted message"
    return False
  elif seq_num != expected_seq_num:
    print "The receiver returned an invalid sequence number"
    return False
  return True

#Seq_num should be the send_message seq_num + 1
def recv_ack(sock, seq_num, message, dst_ip):
  global T_OFFLINE
  global PORT

  counter = 5
  while True:
    try:
      data,addr = sock.recvfrom(5020)
      if data is not None: 
        counter = 5
      return check_seq_error(seq_num, data)
    except socket.timeout:
      if counter >= T_OFFLINE:
        print "The receiver is not online"
        exit(1)
      send_message(sock, dst_ip, message, seq_num-1)
      counter += T_DELAY

def main():
  global T_DELAY
  global T_OFFLINE
  global PORT

  ip_addr, text_file = get_arguments()
  data = get_textfile_blocks(text_file)
  socket = init_socket(T_DELAY)
  for x in xrange(len(data)-1):
    send_message(socket, ip_addr, data[x], x)
    while recv_ack(socket, x+1, data[x], ip_addr) is not True:
      send_message(socket, ip_addr, data[x], x)

  send_fin_message(socket, ip_addr, data[-1])
  while recv_ack(socket, 0, data[-1], ip_addr) is not True:
    send_fin_message(socket, ip_addr, data[-1])
  print "Sent %s successfully" % text_file

if __name__ == "__main__":
    main()
