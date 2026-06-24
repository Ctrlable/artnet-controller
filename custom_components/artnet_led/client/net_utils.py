import socket
from netifaces import gateways,AF_INET
def get_default_gateway():return gateways()['default'][AF_INET][0]
def get_private_ip():
	A=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);A.settimeout(0)
	try:A.connect(('10.254.254.254',1));return A.getsockname()[0]
	except Exception:return'127.0.0.1'
	finally:A.close()