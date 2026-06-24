from __future__ import annotations
import asyncio,logging,socket
from typing import Any
from.client import ArtPoll,ArtPollReply
from.const import ARTNET_DEFAULT_PORT
_LOGGER=logging.getLogger(__name__)
DISCOVERY_TIMEOUT=3.
class _ArtPollProtocol(asyncio.DatagramProtocol):
	def __init__(A):A.nodes={}
	def datagram_received(F,data,addr):
		E='\x00 ';A=addr[0];B=ArtPollReply();C='';D=''
		try:B.deserialize(bytearray(data));C=(B.short_name or'').strip(E).strip();D=(B.long_name or'').strip(E).strip()
		except Exception:_LOGGER.debug('Ignoring non-ArtPollReply datagram from %s',A)
		G=D or C or f"Art-Net node @ {A}";F.nodes.setdefault(A,{'host':A,'short_name':C,'long_name':D,'title':G})
async def async_discover(timeout=DISCOVERY_TIMEOUT):
	D=asyncio.get_running_loop();A=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);A.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);A.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
	try:A.bind(('',ARTNET_DEFAULT_PORT))
	except OSError as E:A.close();_LOGGER.warning('Art-Net discovery could not bind UDP/%s (%s); is a node already running on this host? Returning no results.',ARTNET_DEFAULT_PORT,E);return[]
	B,F=await D.create_datagram_endpoint(_ArtPollProtocol,sock=A)
	try:G=bytes(ArtPoll().serialize());B.sendto(G,('255.255.255.255',ARTNET_DEFAULT_PORT));await asyncio.sleep(timeout)
	finally:B.close()
	C=list(F.nodes.values());_LOGGER.debug('Art-Net discovery found %d node(s)',len(C));return C