import logging
from array import array
from typing import Optional,Callable,Collection,Union,Type,List,Literal
from pyartnet import Channel,BaseUniverse
from pyartnet.fades import FadeBase,LinearFade
log=logging.getLogger('pyartnet.Channel')
class ChannelBridge:
	def __init__(A,channel):A.__channel=channel;A.callback_values_updated=None
	def _apply_output_correction(A):A.__channel._apply_output_correction()
	def get_values(A):return A.__channel.get_values()
	def set_values(A,values):return A.__channel.set_values(values)
	def to_buffer(A,buf):return A.__channel.to_buffer(buf)
	def add_fade(A,values,duration_ms,fade_class=LinearFade):return A.__channel.add_fade(values,duration_ms,fade_class)
	def set_fade(A,values,duration_ms,fade_class=LinearFade):return A.__channel.set_fade(values,duration_ms,fade_class)
	def __await__(A):return A.__channel.__await__()
	def __repr__(A):return A.__channel.__repr__()
	def set_output_correction(A,func):A.__channel.set_output_correction(func)
	@property
	def _start(self):return self.__channel._start
	@property
	def _width(self):return self.__channel._width
	@property
	def _stop(self):return self.__channel._stop
	@property
	def _byte_size(self):return self.__channel._byte_size
	@property
	def _byte_order(self):return self.__channel._byte_order
	@property
	def _value_max(self):return self.__channel._value_max
	@property
	def _buf_start(self):return self.__channel._buf_start
	@property
	def _parent_universe(self):return self.__channel._parent_universe
	@property
	def _parent_node(self):return self.__channel._parent_node
	@property
	def _current_fade(self):return self.__channel._current_fade
	@property
	def callback_fade_finished(self):return self.__channel.callback_fade_finished
	@property
	def _correction_current(self):return self.__channel._correction_current
	@property
	def _values_raw(self):return self.__channel._values_raw
	@property
	def _values_act(self):return self.__channel._values_act
	@callback_fade_finished.setter
	def callback_fade_finished(self,value):self.__channel.callback_fade_finished=value
	@_correction_current.setter
	def _correction_current(self,value):self.__channel._correction_current=value
	@_values_raw.setter
	def _values_raw(self,value):self.__channel._values_raw=value
	@_values_act.setter
	def _values_act(self,value):self.__channel._values_act=value
	def from_buffer(A,buf):
		H=False;I=A.__channel._byte_order;C=A.__channel._byte_size;F=A.__channel._start-1;J=A.__channel._stop;K=A.__chunks(buf[F:J],C);B=array('i',[int.from_bytes(A,I,signed=H)for A in K if len(A)==C]);B=B+array(B.typecode,[-1]*(len(A.__channel._values_act)-len(B)));G=H
		for(D,E)in enumerate(B):
			if E==-1:log.warning(f"Channel {F+D} was updated externally, but is part of an incomplete {C} byte number. This is very likely unintended by the external controller.");break
			if A.__channel._values_act[D]==E:continue
			A.__channel._values_act[D]=E;G=True
		if not G:return
		L=[A for A in B]
		for(M,N)in enumerate(L):A.__channel._values_raw[M]=N
		if A.callback_values_updated is not None:A.callback_values_updated(A.__channel._values_raw)
	@staticmethod
	def __chunks(lst,n):
		for A in range(0,len(lst),n):yield lst[A:A+n]