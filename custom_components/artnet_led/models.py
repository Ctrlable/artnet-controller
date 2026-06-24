from __future__ import annotations
_D='invalid_output_correction'
_C='dimmer'
_B='8bit'
_A=None
from dataclasses import dataclass
from typing import Any
from.const import BYTE_ORDERS,CHANNEL_SIZES,DEVICE_DEFAULTS,DEVICE_TYPES,DMX_UNIVERSE_SIZE,NODE_TYPES,OPT_DEV_BYTE_ORDER,OPT_DEV_CHANNEL,OPT_DEV_CHANNEL_SETUP,OPT_DEV_CHANNEL_SIZE,OPT_DEV_NAME,OPT_DEV_TYPE,OPT_MAX_FPS,OPT_NODE,OPT_NODE_TYPE,OPT_PORT,OPT_REFRESH_EVERY,OPT_UNI_DEVICES,OPT_UNI_NAME,OPT_UNI_OUTPUT_CORRECTION,OPT_UNI_SEND_PARTIAL,OPT_UNIVERSES,OUTPUT_CORRECTIONS
CHANNEL_SIZE_BYTES={_B:1,'16bit':2,'24bit':3,'32bit':4}
TYPE_DEFAULT_WIDTH={_C:1,'binary':1,'fixed':1,'rgb':3,'color_temp':2,'rgbw':4,'rgbww':5,'xy':3}
class OptionsValidationError(Exception):
	def __init__(B,error_key,message=_A):A=error_key;super().__init__(message or A);B.error_key=A
@dataclass(slots=True)
class _Slot:start:int;end:int;name:str
def logical_width(device):
	B=device;A=B.get(OPT_DEV_CHANNEL_SETUP)
	if isinstance(A,str)and A:return len(A)
	if isinstance(A,(list,tuple))and A:return len(A)
	return TYPE_DEFAULT_WIDTH.get(B.get(OPT_DEV_TYPE,_C),1)
def slot_footprint(device):A=device;B=A.get(OPT_DEV_CHANNEL_SIZE)or _B;return logical_width(A)*CHANNEL_SIZE_BYTES.get(B,1)
def apply_device_defaults(device):A={**DEVICE_DEFAULTS,**device};return A
def _validate_node(node):
	A=node;C=A.get(OPT_NODE_TYPE,'artnet-direct')
	if C not in NODE_TYPES:raise OptionsValidationError('invalid_node_type',f"Unknown node_type {C!r}")
	B=A.get(OPT_PORT)
	if B is not _A and not 1<=int(B)<=65535:raise OptionsValidationError('invalid_port',f"Port {B} out of range")
	D=A.get(OPT_MAX_FPS,25)
	if not 1<=int(D)<=50:raise OptionsValidationError('invalid_max_fps','max_fps must be 1..50')
	E=A.get(OPT_REFRESH_EVERY,120)
	if float(E)<0:raise OptionsValidationError('invalid_refresh','refresh_every must be >= 0')
def _validate_device(uni_nr,device):
	A=device
	if OPT_DEV_NAME not in A or not str(A[OPT_DEV_NAME]).strip():raise OptionsValidationError('missing_name','Each fixture needs a name')
	B=A.get(OPT_DEV_TYPE,_C)
	if B not in DEVICE_TYPES:raise OptionsValidationError('invalid_type',f"Unknown fixture type {B!r}")
	C=A.get(OPT_DEV_CHANNEL)
	if C is _A or not 1<=int(C)<=DMX_UNIVERSE_SIZE:raise OptionsValidationError('invalid_channel',f"Channel must be 1..{DMX_UNIVERSE_SIZE}")
	D=A.get(OPT_DEV_CHANNEL_SIZE,_B)
	if D not in CHANNEL_SIZES:raise OptionsValidationError('invalid_channel_size',f"Unknown channel_size {D!r}")
	E=A.get(OPT_DEV_BYTE_ORDER,'big')
	if E not in BYTE_ORDERS:raise OptionsValidationError('invalid_byte_order',f"Unknown byte_order {E!r}")
	F=A.get('output_correction')
	if F not in(_A,*OUTPUT_CORRECTIONS):raise OptionsValidationError(_D,f"Unknown output_correction {F!r}")
def validate_options(options):
	K='invalid_universe';F=options;L=F.get(OPT_NODE,{})or{};_validate_node(L);M=F.get(OPT_UNIVERSES,{})or{}
	for(G,H)in M.items():
		try:B=int(G)
		except(TypeError,ValueError)as N:raise OptionsValidationError(K,f"Universe key {G!r} is not an integer")from N
		if not 0<=B<=32767:raise OptionsValidationError(K,f"Universe {B} out of range")
		I=H.get(OPT_UNI_OUTPUT_CORRECTION,'linear')
		if I not in(_A,*OUTPUT_CORRECTIONS):raise OptionsValidationError(_D,f"Unknown output_correction {I!r}")
		J=[]
		for A in H.get(OPT_UNI_DEVICES,[])or[]:
			_validate_device(B,A);E=int(A[OPT_DEV_CHANNEL]);C=E+slot_footprint(A)-1
			if C>DMX_UNIVERSE_SIZE:raise OptionsValidationError('overflow',f"Fixture {A.get(OPT_DEV_NAME)!r} runs to channel {C}, past the {DMX_UNIVERSE_SIZE}-slot universe {B}")
			for D in J:
				if E<=D.end and D.start<=C:raise OptionsValidationError('overlap',f"Fixture {A.get(OPT_DEV_NAME)!r} (ch {E}-{C}) overlaps {D.name!r} (ch {D.start}-{D.end}) in universe {B}")
			J.append(_Slot(E,C,str(A.get(OPT_DEV_NAME))))
	return F
def count_fixtures(options):A=options.get(OPT_UNIVERSES,{})or{};return sum(len(A.get(OPT_UNI_DEVICES,[])or[])for A in A.values())
def default_options():from.const import DEFAULT_NODE as A;return{OPT_NODE:dict(A),OPT_UNIVERSES:{}}