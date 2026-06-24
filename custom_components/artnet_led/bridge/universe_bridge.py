from typing import Literal
from pyartnet import BaseUniverse
from custom_components.artnet_led.bridge.channel_bridge import ChannelBridge
class UniverseBridge(BaseUniverse):
	def receive_data(A,data):
		B=A._channels
		for C in B.values():C.from_buffer(data)
	def add_channel(C,start,width,channel_name='',byte_size=1,byte_order='big'):A=channel_name;B=ChannelBridge(super().add_channel(start,width,A,byte_size,byte_order));C._channels[A]=B;return B