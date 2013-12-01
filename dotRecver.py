#!/usr/bin/env python
import struct
import socket
import hashlib
from multiprocessing import Process, Queue
from time import time

MAX_UINT = 0xffffffff

def write_p(queue, fname):
  with open(fname, "w") as fp:
    while True:
      data = queue.get()
      fp.write(data)
      

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

def main():
    global MAX_UINT
    mysock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_to_write = {}

    mysock.bind(('127.0.0.1', 31337))
    prev_seq_num = 0
    prev_message = ""

    while True:
        data, addr = mysock.recvfrom(5020)
        seq_num, msg_hash, message = extract_message_contents(data)
        #print "DATA_LENGTH: ", len(data)
        #print "SEQ_NUM: ", seq_num
        #print "MSG_HASH: ", msg_hash.encode('hex')
        #print "Message: ", message
        is_valid_hash = check_hash(message, msg_hash)
        print "SEQ_NUM: ", seq_num
        if seq_num == 0 and is_valid_hash == True: #We don't want to make a process if file is corrupt!
          print "Making new process...."
          write_queue = Queue()
          write_process = Process(target=write_p, args = (write_queue, "recvEmail_%d"%int(time())))
          write_process.start()

        if prev_seq_num == seq_num: #The receiver re-sent due to corruption
          prev_message = message

        if prev_seq_num < seq_num: #We have a new sequence, the previous message was correct
          write_queue.put(prev_message)
          prev_message = message
          prev_seq_num = seq_num #make the previous sequence number the new one now

        if seq_num == MAX_UINT:
          seq_num = struct.pack("!I", 0)
          print "Received FIN, sending FIN-ACK"
          while not write_queue.empty():
            pass
          print "EXTERMINATE! EXTERMINATE!!!!"
          prev_seq_num = 0
          prev_message = ""
          write_process.terminate()
        else:
          seq_num = struct.pack("!I", seq_num+1)
        send_ack(addr, mysock, seq_num, is_valid_hash)

if __name__ == "__main__":
    main()
