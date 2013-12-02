import subprocess
import sys
import hashlib
from os import system
from time import sleep

def get_file_names(directory):
  proc = subprocess.Popen(["ls", directory], stdout=subprocess.PIPE)
  return proc.communicate()[0].split("\n")[:-1]

def md5_hash_file(filename):
  with open(filename, 'rb') as f:
    h = hashlib.md5()
    h.update(f.read())
    return h.hexdigest()

def main():
  if len(sys.argv) != 3:
    print "usage: %s [original_filename] [test_directory]"
    exit(1)

  expected_md5 = md5_hash_file(sys.argv[1])
  file_name = sys.argv[1]
  print "RUNNING TEST ON %s" % file_name
  print "USING DOTSENDER"
  for x in xrange(25):
    proc = subprocess.Popen(['python', 'dotSender.py', '127.0.0.1', file_name])
    proc.wait()
    #system('python dotSender.py 127.0.0.1 ' + file_name)
  system('mv recvEmail* recv_tests/')
  print "END DOTSENDER"
  sleep(1)

  print "BEGIN CHECKING MD5SUMS"
  for f in get_file_names(sys.argv[2]):
    print "Testing file %s" % f
    if md5_hash_file(sys.argv[2] + "/" + f) != expected_md5:
      print "File %s does not match." % f
      system("diff -u %s %s/%s" % (sys.argv[1], sys.argv[2], f))      
  print "END MD5SUM CHECKING"

if __name__ == "__main__":
  main()
