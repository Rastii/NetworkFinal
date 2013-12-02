from struct import pack
import socket
import hashlib
from random import random

MAX_UINT = 0xffffffff
SERVER_IP = '127.0.0.1'
SERVER_PORT = 31337

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 31338))

def extract_message_contents(message):
  return (struct.unpack("!I", message[0:4])[0], 
          message[4:20], 
          message[20:])


loops = 1
while True:
  #first we receive from the sender
  data, client_addr = sock.recvfrom(5020)

  if int(random()*2) & 1 == 1: #let's modify some bits..
    random_val = int(random()*len(data))-1
    data = data[0:random_val] + pack("!B",int(random()*255)) + data[random_val:]
  #now send to our server
  sock.sendto(data, (SERVER_IP,SERVER_PORT))

  #Now we'll receive from the server
  data, addr = sock.recvfrom(5020)

  #Let's just forward this data to the client...
  sock.sendto(data, client_addr)
  print "Net Loops completed: %d" % loops
  loops += 1
