import subprocess
import sys
import hashlib

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

  for f in get_file_names(sys.argv[2]):
    print "Testing file %s" % f
    if md5_hash_file(sys.argv[2] + "/" + f) != expected_md5:
      print "File %s does not match." % f
      exit(1)

if __name__ == "__main__":
  main()
