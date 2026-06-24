import logging
from asyncio import sleep
from homeassistant.core import HomeAssistant
from pyartnet import BaseUniverse
from pyartnet.base import BaseNode
from pyartnet.base.network import UnicastNetworkTarget
from pyartnet.errors import InvalidUniverseAddressError
from custom_components.artnet_led.bridge.universe_bridge import UniverseBridge
from custom_components.artnet_led.client import PortAddress
from custom_components.artnet_led.client.artnet_server import ArtNetServer
log=logging.getLogger(__name__)
HA_OEM=11241
class ArtNetController(BaseNode):
	def __init__(A,hass,max_fps=25,refresh_every=2):super().__init__(UnicastNetworkTarget.create('127.0.0.1',6454),max_fps=max_fps,refresh_every=0);A._hass=hass;A.__server=ArtNetServer(hass,state_update_callback=A.update_dmx_data,oem=HA_OEM,short_name='ha-artnet-led',long_name='HomeAssistant ArtNet integration',retransmit_time_ms=int(refresh_every*1e3))
	def _send_universe(B,id,byte_size,values,universe):A=PortAddress.parse(id);log.debug(f"Going to send to port address {A}");B.__server.send_dmx(A,universe._data)
	def _validate_universe_nr(A,nr):
		if not isinstance(nr,int)or nr<0:raise ValueError('Universe must be an int >= 0!')
		if nr>=32768:raise InvalidUniverseAddressError()
		return int(nr)
	def _create_universe(A,nr):return UniverseBridge(A,A._validate_universe_nr(nr))
	def add_universe(A,nr=0):B=super().add_universe(nr);A.__server.add_port(PortAddress.parse(nr));return B
	def start(A):return A.__server.start_server()
	def get_universe(A,nr):return super().get_universe(nr)
	def update_dmx_data(A,address,data):A.get_universe(address.port_address).receive_data(data)
	async def _process_values_task(B):
		log.debug(f"Processing values changed");C=0
		while C<10:
			C+=1;D=[]
			for A in B._process_jobs:
				A.process();C=0
				if A.is_done:D.append(A)
			for E in B._universes:
				if not E._data_changed:continue
				E.send_data();C=0
			if D:
				for A in D:B._process_jobs.remove(A);A.fade_complete()
			await sleep(B._process_every)