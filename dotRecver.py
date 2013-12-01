#!/usr/bin/env python
import struct
import socket
import hashlib
from multiprocessing import Process, Queue
from time import time

MAX_UINT = 0xffffffff
CONNECTION = {}

def write_p(queue, fname):
  global MAX_UINT
  with open(fname, "w") as fp:
    while True:
      data = queue.get()
      fp.write(data['message'])
      if data['seq'] == MAX_UINT:
        exit(0)

def check_hash(message,message_hash):
  h = hashlib.md5()
  h.update(message)
  if h.digest() == message_hash:
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

def create_queue_and_process(the_time):
  print "Creating process!"
  write_queue = Queue()
  write_process = Process(target=write_p, args=(write_queue, "recvEmail_%d"%the_time))
  write_process.start()
  return (write_queue, write_process)

def main():
    global MAX_UINT
    global CONNECTION
    mysock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_to_write = {}

    mysock.bind(('127.0.0.1', 31337))
    prev_seq_num = 0
    prev_message = ""

    while True:
        data, addr = mysock.recvfrom(5020)
        if addr not in CONNECTION:
          print "Connection established from %s" % addr[0]
          now = int(time())
          CONNECTION[addr] = now
          write_queue, write_process = create_queue_and_process(now)

        seq_num, msg_hash, message = extract_message_contents(data)
        is_valid_hash = check_hash(message, msg_hash)

        if prev_seq_num == seq_num: #The receiver re-sent due to corruption
          prev_message = message

        if prev_seq_num == seq_num-1 or seq_num == MAX_UINT: #new sequence, previous message was correct!
          write_queue.put({'seq': prev_seq_num, 'message':prev_message})
          prev_message = message
          prev_seq_num = seq_num #make the previous sequence number the new one now

        if seq_num == MAX_UINT:
          seq_num = struct.pack("!I", 0)
          if is_valid_hash == True: #If the hash is not valid, the sender _should_ resend the FIN
            write_queue.put({'seq': MAX_UINT, 'message':message})
            prev_seq_num = 0 #reset previous sequence number
            prev_message = "" #reset previous message to original state
            CONNECTION = {} #reset connection!
            write_process.join() #wait for process to close!
            print "Finished writing email to file"
        else:
          seq_num = struct.pack("!I", seq_num+1)
        send_ack(addr, mysock, seq_num, is_valid_hash)

if __name__ == "__main__":
    main()
