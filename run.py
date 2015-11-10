#!/usr/bin/python
import sys, getopt

from Robinhood import RobinhoodExporter

def main(argv):

  username = None
  password = None
  outfile = None

  try:
    opts, args = getopt.getopt(argv,"hu:p:f:",["username=","password=", "file="])
  except getopt.GetoptError:
    print 'run.py -u <username> -p <password> -f <outputfile>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'run.py -u <username> -p <password> -f <outputfile>'
      sys.exit()
    elif opt in ("-u", "--username"):
      username = arg
    elif opt in ("-p", "--password"):
      password = arg
    elif opt in ("-f", "--file"):
      outfile = arg

  rh = RobinhoodExporter(username, password, filename=outfile)
  rh.to_csv()

if __name__ == "__main__":
  main(sys.argv[1:])