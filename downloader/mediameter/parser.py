import socket
import logging
import json

log = logging.getLogger('mediacloud')
parser_socket = None
parser_socket_file = None

def connect(host="127.0.0.1", port=4000):
    global parser_socket, parser_socket_file, log
    try:
      parser_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      parser_socket.connect((host, port))
      parser_socket_file = parser_socket.makefile('r') 
    except socket.error, msg:
      log.error("ParseServer: Unable to connect to server at "+host+":"+str(port))
      log.error(msg[1])
      return False
    log.info("ParseServer: Connected to server at "+host+":"+str(port))
    return True

def parse(text):
    parser_socket.send(text.encode('utf-8')+"\n")
    byte_count = 0
    results = parser_socket_file.readline()
    log.info("ParseServer: received "+str(len(results))+" bytes of from a parse request")
    log.info(results)
    return json.loads(results)

def close():
    global parser_socket
    parser_socket.close()
    log.info("Closed ParseServer server")
