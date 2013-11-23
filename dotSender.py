#!/usr/bin/env python
import socket
import sys


def get_arguments():
    if len(sys.argv) != 3:
      print "Usage: ./%s [ip] [file]"
      exit(1)
    return (sys.argv[1], sys.argv[2])

def get_textfile_blocks(text_file):
  try:
    with f as open(text_file, 'r'):
      data = f.read()
      blocks, remainder = divmod(len(data), 5000)
      return [data[x*5000:(x+1)*5000] for x in blocks] \
             + data[(blocks*5000)-1:]
  except:
    print "Invalid file specifi1ed -- unable to open file"

def main():
    ip_addr, text_file = get_arguments()
    print get_textfile_blocks(text_file)
    
  

if __name__ == "__main__":
    main()
