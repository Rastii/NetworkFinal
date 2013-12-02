#!/usr/bin/env python
# ====================================== file=dotRecver.py ====
# =  Program runs as daemon, receives emails from client      =
# =============================================================
# =  Notes:                                                   =
# =    1) Client assumes server runs on port 31337, don't     =
# =       change unless you are certain client knows          =
# =    2) Emails will be written to recvEmail_[timestamp]     =
# =       where timestamp is unix time in milliseconds        =
# =    3) File is sent in chunks of 5000 bytes                =
# =-----------------------------------------------------------=
# =  Bugs: None known                                         =
# =-----------------------------------------------------------=
# =  Build: Not necessary, python is interpreted              =
# =-----------------------------------------------------------=
# =  Execute: ./dotRecver.py                                  =
# =-----------------------------------------------------------=
# =  Authors: Andrew Calvano, Lukyan Hritsko                  =
# =           University of South Florida                     =
# ==== Main Program ===========================================

import struct
import socket
import hashlib
from multiprocessing import Process, Queue
from time import time

MAX_UINT = 0xffffffff
T_OFFLINE = 20
CONNECTION = {}

def write_p(queue, fname):
  global MAX_UINT
  with open('emails/' + fname, "w") as fp:
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
  try:
    return (struct.unpack("!I", message[0:4])[0], 
            message[4:20], 
            message[20:])
  except:
    return (None,None,None)

def send_ack(addr, sock, seq_num, is_valid_hash):
  if is_valid_hash is True:
    sock.sendto(seq_num + struct.pack("!B", 0),addr)
  else:
    sock.sendto(seq_num + struct.pack("!B", 1),addr)

def create_queue_and_process(the_time):
  filename = "recvEmail_%d.txt"%the_time
  print "Writing email to: %s" % filename
  write_queue = Queue()
  write_process = Process(target=write_p, args=(write_queue, filename))
  write_process.start()
  return (write_queue, write_process)

def main():
    global MAX_UINT
    global CONNECTION
    global T_OFFLINE

    mysock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_to_write = {}

    mysock.bind(('0.0.0.0', 31337))
    print "Waiting for a POLL/Message"
    prev_seq_num = 0
    prev_message = ""

    while True:
      try:
        data, addr = mysock.recvfrom(5020)
        if addr not in CONNECTION:
          mysock.settimeout(T_OFFLINE)
          print "Connection established from %s" % addr[0]
          now = int(round(time() * 1000))
          CONNECTION[addr] = now
          write_queue, write_process = create_queue_and_process(now)

        seq_num, msg_hash, message = extract_message_contents(data)
        if seq_num is None: raise socket.timeout
        is_valid_hash = check_hash(message, msg_hash)

        if prev_seq_num == seq_num: #The receiver re-sent due to corruption or POLL packet
          prev_message = message

        #if prev_seq_num == seq_num-1 or seq_num == MAX_UINT: #new sequence, previous message was correct!
        if prev_seq_num == seq_num-1:  #new sequence, previous message was correct!
          write_queue.put({'seq': prev_seq_num, 'message':prev_message})
          prev_message = message
          prev_seq_num = seq_num #make the previous sequence number the new one now

        if seq_num == MAX_UINT:
          if prev_message != "":
            write_queue.put({'seq': prev_seq_num, 'message': prev_message})
            prev_message = ""
          seq_num = struct.pack("!I", 0)
          if is_valid_hash == True: #If the hash is not valid, the sender _should_ resend the FIN
            h = hashlib.md5()
            h.update(message)
            write_queue.put({'seq': MAX_UINT, 'message':message})
            prev_seq_num = 0 #reset previous sequence number
            prev_message = "" #reset previous message to original state
            CONNECTION = {} #reset connection!
            write_process.join() #wait for process to close!
            print "SUCCESS -- email received and finished writing to the file"
            print "--------------------------"
            print "Waiting for a POLL/Message"
        else:
          seq_num = struct.pack("!I", seq_num+1)
        send_ack(addr, mysock, seq_num, is_valid_hash)
      except socket.timeout:
        print "Connection timed out with receiver, or packets were invalid, email may not be complete."
        print "--------------------------"
        print "Waiting for a POLL/Message"
        mysock.settimeout(None)
        if write_process: write_process.terminate()
        CONNECTION = {}
        prev_seq_num = 0
        prev_message = ""

if __name__ == "__main__":
    main()
