from __future__ import annotations
_J='\\d+(k|K)'
_I='dimmer'
_H='artnet-controller'
_G='artnet-direct'
_F='linear'
_E=False
_D='values'
_C='bright'
_B=True
_A=None
import asyncio,logging,time
from array import array
from typing import Union
import homeassistant.helpers.config_validation as cv,homeassistant.util.color as color_util
from homeassistant.util import slugify
import pyartnet,voluptuous as vol
from homeassistant.components.light import ATTR_BRIGHTNESS,ATTR_RGB_COLOR,ATTR_RGBW_COLOR,ATTR_RGBWW_COLOR,ATTR_XY_COLOR,ATTR_TRANSITION,PLATFORM_SCHEMA,LightEntity,ATTR_WHITE,ATTR_COLOR_TEMP_KELVIN,ATTR_FLASH,FLASH_SHORT,FLASH_LONG,ATTR_HS_COLOR,LightEntityFeature,ColorMode
from homeassistant.const import CONF_DEVICES,STATE_OFF,STATE_ON
from homeassistant.const import CONF_FRIENDLY_NAME as CONF_DEVICE_FRIENDLY_NAME
from homeassistant.const import CONF_HOST as CONF_NODE_HOST
from homeassistant.const import CONF_NAME as CONF_DEVICE_NAME
from homeassistant.const import CONF_PORT as CONF_NODE_PORT
from homeassistant.const import CONF_TYPE as CONF_DEVICE_TYPE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util.color import color_rgb_to_rgbw
from pyartnet import BaseUniverse,Channel
from pyartnet.errors import UniverseNotFoundError
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from custom_components.artnet_led.bridge.artnet_controller import ArtNetController
from custom_components.artnet_led.bridge.channel_bridge import ChannelBridge
from custom_components.artnet_led.util.channel_switch import validate,to_values,from_values
from custom_components.artnet_led.const import DOMAIN as INTEGRATION_DOMAIN,PANEL_URL_PATH,DEFAULT_NODE,OPT_NODE,OPT_UNIVERSES,OPT_PORT,OPT_NODE_TYPE,OPT_MAX_FPS,OPT_REFRESH_EVERY,OPT_UNI_SEND_PARTIAL,OPT_UNI_OUTPUT_CORRECTION,OPT_UNI_DEVICES
from custom_components.artnet_led.models import apply_device_defaults
ARTNET_DEFAULT_PORT=6454
SACN_DEFAULT_PORT=5568
KINET_DEFAULT_PORT=6038
CONF_DEVICE_TRANSITION=ATTR_TRANSITION
CONF_SEND_PARTIAL_UNIVERSE='send_partial_universe'
log=logging.getLogger(__name__)
CONF_NODE_HOST_OVERRIDE='host_override'
CONF_NODE_PORT_OVERRIDE='port_override'
CONF_NODE_TYPE='node_type'
CONF_NODE_MAX_FPS='max_fps'
CONF_NODE_REFRESH='refresh_every'
CONF_NODE_UNIVERSES='universes'
CONF_DEVICE_CHANNEL='channel'
CONF_OUTPUT_CORRECTION='output_correction'
CONF_CHANNEL_SIZE='channel_size'
CONF_BYTE_ORDER='byte_order'
CONF_DEVICE_MIN_TEMP='min_temp'
CONF_DEVICE_MAX_TEMP='max_temp'
CONF_CHANNEL_SETUP='channel_setup'
DOMAIN='dmx'
AVAILABLE_CORRECTIONS={_F:pyartnet.output_correction.linear,'quadratic':pyartnet.output_correction.quadratic,'cubic':pyartnet.output_correction.cubic,'quadruple':pyartnet.output_correction.quadruple}
type LogicalChannelSize=int
type LogicalChannelNumBytes=int
type ChannelSize=tuple[LogicalChannelSize,LogicalChannelNumBytes]
CHANNEL_SIZE={'8bit':(1,1),'16bit':(2,256),'24bit':(3,256**2),'32bit':(4,256**3)}
NODES={}
async def async_setup_platform(hass,config,async_add_devices,discovery_info=_A):await _async_setup_node(hass,config,async_add_devices);return _B
async def async_setup_entry(hass,entry,async_add_entities):
	A=entry;D=A.data[CONF_NODE_HOST];B={**DEFAULT_NODE,**(A.options or{}).get(OPT_NODE,{})};E={CONF_NODE_HOST:D,CONF_NODE_HOST_OVERRIDE:'',CONF_NODE_PORT:B[OPT_PORT],CONF_NODE_PORT_OVERRIDE:_A,CONF_NODE_TYPE:B[OPT_NODE_TYPE],CONF_NODE_MAX_FPS:B[OPT_MAX_FPS],CONF_NODE_REFRESH:B[OPT_REFRESH_EVERY],CONF_NODE_UNIVERSES:{}}
	for(F,C)in(A.options or{}).get(OPT_UNIVERSES,{}).items():E[CONF_NODE_UNIVERSES][int(F)]={CONF_SEND_PARTIAL_UNIVERSE:C.get(OPT_UNI_SEND_PARTIAL,_B),CONF_OUTPUT_CORRECTION:C.get(OPT_UNI_OUTPUT_CORRECTION,_F),CONF_DEVICES:[apply_device_defaults(A)for A in C.get(OPT_UNI_DEVICES,[])]}
	G=DeviceInfo(identifiers={(INTEGRATION_DOMAIN,D)},name=A.title,manufacturer='Ctrlable',configuration_url=f"homeassistant://{PANEL_URL_PATH}");await _async_setup_node(hass,E,async_add_entities,device_info=G,entry=A);return _B
async def _async_setup_node(hass,config,async_add_devices,device_info=_A,entry=_A):
	V=device_info;S=entry;R='server';E=config;pyartnet.base.background_task.CREATE_TASK=asyncio.create_task;I=E.get(CONF_NODE_TYPE);N=E.get(CONF_NODE_MAX_FPS);G=E.get(CONF_NODE_REFRESH);J=E.get(CONF_NODE_HOST);K=E.get(CONF_NODE_PORT);L=E.get(CONF_NODE_HOST_OVERRIDE)
	if len(L)==0:L=J
	B=E.get(CONF_NODE_PORT_OVERRIDE)
	if B==_A:B=K
	F:0
	if I==_G:
		if B is _A:B=ARTNET_DEFAULT_PORT
		C=f"{J}:{K}"
		if C not in NODES:
			from pyartnet.base.network import UnicastNetworkTarget as M;A=pyartnet.ArtNetNode(M.create(L,B),max_fps=N,refresh_every=G);await A.__aenter__()
			if not G:await A.stop_refresh()
			NODES[C]=A
		F=NODES[C]
	elif I==_H:
		if R not in NODES:A=ArtNetController(hass,max_fps=N,refresh_every=G);NODES[R]=A;A.start()
		F=NODES[R]
	elif I=='sacn':
		if B is _A:B=SACN_DEFAULT_PORT
		C=f"{J}:{K}"
		if C not in NODES:
			from pyartnet.base.network import UnicastNetworkTarget as M;A=pyartnet.SacnNode(M.create(L,B),max_fps=N,refresh_every=G,source_name='ha-artnet-led');await A.__aenter__()
			if not G:await A.stop_refresh()
			NODES[C]=A
		F=NODES[C]
	elif I=='kinet':
		if B is _A:B=KINET_DEFAULT_PORT
		C=f"{J}:{K}"
		if C not in NODES:
			from pyartnet.base.network import UnicastNetworkTarget as M;A=pyartnet.KiNetNode(M.create(L,B),max_fps=N,refresh_every=G);await A.__aenter__()
			if not G:await A.stop_refresh()
			NODES[C]=A
		F=NODES[C]
	else:raise NotImplementedError(f"Unknown client type '{I}'")
	if S is not _A:
		S.runtime_data=F;a=R if I==_H else f"{J}:{K}"
		async def b(_node=F,_key=a):
			A=_node;NODES.pop(_key,_A)
			try:
				if hasattr(A,'__aexit__'):await A.__aexit__(_A,_A,_A)
				elif hasattr(A,'stop'):
					B=A.stop()
					if asyncio.iscoroutine(B):await B
			except Exception as C:log.warning('Error tearing down Art-Net node %s: %s',_key,C)
		S.async_on_unload(b)
	c=async_get(hass);W=[];X=[]
	for(T,U)in E[CONF_NODE_UNIVERSES].items():
		try:O=F.get_universe(T)
		except UniverseNotFoundError:O=F.add_universe(T);O.set_output_correction(AVAILABLE_CORRECTIONS.get(U[CONF_OUTPUT_CORRECTION]))
		for D in U[CONF_DEVICES]:
			D=D.copy();d=__CLASS_TYPE[D[CONF_DEVICE_TYPE]];Y=D[CONF_DEVICE_CHANNEL];P=f"{DOMAIN}:{J}/{T}/{Y}";e=D[CONF_DEVICE_NAME];f=CHANNEL_SIZE[D[CONF_CHANNEL_SIZE]][0];g=D[CONF_BYTE_ORDER];Z=f"light.{slugify(e)}";Q=c.async_get(Z)
			if Q:
				log.info(f"Found existing entity for name {Z}, using unique id {P}")
				if Q.unique_id is not _A and Q.unique_id not in X:P=Q.unique_id
			X.append(P);D['unique_id']=P;H=d(**D);H.set_type(D[CONF_DEVICE_TYPE]);H.set_channel(O.add_channel(start=Y,width=H.channel_width,channel_name=H.name,byte_size=f,byte_order=g));H.channel.set_output_correction(AVAILABLE_CORRECTIONS.get(D[CONF_OUTPUT_CORRECTION]))
			if V is not _A:H._attr_device_info=V
			W.append(H);h=U[CONF_SEND_PARTIAL_UNIVERSE]
			if not h:O._resize_universe(512)
	async_add_devices(W);return _B
def convert_to_kelvin(kelvin_string):return int(kelvin_string[:-1])
class DmxBaseLight(LightEntity,RestoreEntity):
	def __init__(A,name,unique_id,**B):A._name=name;A._channel=B[CONF_DEVICE_CHANNEL];A._unique_id=unique_id;A.entity_id=f"light.{slugify(name)}";A._attr_brightness=255;A._fade_time=B[CONF_DEVICE_TRANSITION];A._state=_E;A._channel_size=CHANNEL_SIZE[B[CONF_CHANNEL_SIZE]];A._color_mode=B[CONF_DEVICE_TYPE];A._vals=[];A._features=LightEntityFeature(0);A._supported_color_modes=set();A._channel_last_update=0;A._channel_width=0;A._type=_A;(A._channel):0
	def set_channel(A,channel):
		B=channel;A._channel=B;A._channel.callback_fade_finished=A._channel_fade_finish
		if isinstance(B,ChannelBridge):B.callback_values_updated=A._update_values
	def set_type(A,type):A._type=type
	@property
	def name(self):return self._name
	@property
	def unique_id(self):return self._unique_id
	@property
	def color_mode(self):return self._color_mode
	@property
	def supported_features(self):return self._features
	@property
	def extra_state_attributes(self):A=self;B={'type':A._type,'dmx_channels':[A for A in range(A._channel._start,A._channel._start+A._channel._width,1)],'dmx_values':A._channel.get_values(),_D:A._vals,_C:A._attr_brightness};A._channel_last_update=time.time();return B
	@property
	def is_on(self):return self._state
	@property
	def should_poll(self):return _E
	@property
	def supported_color_modes(self):return self._supported_color_modes
	@property
	def fade_time(self):return self._fade_time
	@fade_time.setter
	def fade_time(self,value):self._fade_time=value
	def _update_values(A,values):A._vals=tuple(values);A._channel_value_change()
	def _channel_value_change(A):
		if time.time()-A._channel_last_update>1.1:A._channel_last_update=time.time()
		A.async_schedule_update_ha_state()
	def _channel_fade_finish(A,channel):A._channel_last_update=time.time();A.async_schedule_update_ha_state()
	@staticmethod
	def _default_calculation_function(channel_value):A=channel_value;return A if isinstance(A,int)else 0
	def get_target_values(A):raise NotImplementedError
	async def flash(A,old_values,old_brightness,**F):
		E=old_brightness;D=old_values;B=F.get(ATTR_TRANSITION,A._fade_time)
		if B==0:B=1
		G=A._state;A._state=_B;C=F.get(ATTR_FLASH)
		if G and D==A._vals and E==A._attr_brightness:
			if A._attr_brightness<128:A._attr_brightness=255
			else:A._attr_brightness=0
		if C==FLASH_SHORT:A._channel.set_values(A.get_target_values());await A._channel
		elif C==FLASH_LONG:A._channel.set_fade(A.get_target_values(),B*1000);await A._channel
		else:log.error(f"{C} is not a valid value for attribute {ATTR_FLASH}");return
		A._state=G;A._attr_brightness=E;A._vals=D;A._channel.set_fade(A.get_target_values(),B*1000)
	async def async_create_fade(A,**B):A._state=_B;C=B.get(ATTR_TRANSITION,A._fade_time);A._channel.set_fade(A.get_target_values(),C*1000);A.async_schedule_update_ha_state()
	async def async_turn_off(A,**B):C=B.get(ATTR_TRANSITION,A._fade_time);A._channel.set_fade([0 for A in range(A._channel._width)],C*1000);A._state=_E;A.async_schedule_update_ha_state()
	async def async_added_to_hass(B):
		await super().async_added_to_hass();A=await B.async_get_last_state()
		if A:
			C=A.attributes.get('type')
			if C!=B._type:log.debug('Channel type changed. Unable to restore state.');A=_A
		if A is not _A:await B.restore_state(A)
	async def restore_state(A,old_state):log.error('Derived class should implement this. Report this to the repository author.')
	@property
	def channel_width(self):return self._channel_width
	@property
	def channel_size(self):return self._channel_size
	@property
	def channel(self):return self._channel
class DmxFixed(DmxBaseLight):
	CONF_TYPE='fixed'
	def __init__(A,**B):super().__init__(**B);A._color_mode=ColorMode.ONOFF;A._supported_color_modes.add(ColorMode.ONOFF);A._channel_setup=B.get(CONF_CHANNEL_SETUP)or[255];A._channel_width=len(A._channel_setup)
	def get_target_values(A):return to_values(A._channel_setup,A._channel_size[1],A.is_on,A._attr_brightness)
	def set_channel(B,channel):A=channel;super().set_channel(A);A.set_values(B.get_target_values())
	async def async_turn_on(A,**B):0
	async def async_turn_off(A,**B):0
	async def restore_state(A,old_state):log.debug('Added fixed to hass. Do nothing to restore state. Fixed is constant value');await super().async_create_fade()
class DmxBinary(DmxBaseLight):
	CONF_TYPE='binary'
	def __init__(A,**B):super().__init__(**B);A._channel_width=1;A._features=LightEntityFeature.FLASH;A._color_mode=ColorMode.ONOFF;A._supported_color_modes.add(ColorMode.ONOFF)
	def _update_values(B,values):B._state,A,A,A,A,A,A,C,A,A=from_values('d',B.channel_size[1],values);B._channel_value_change()
	def get_target_values(A):return[A.brightness*A._channel_size[1]]
	async def async_turn_on(A,**B):
		if ATTR_FLASH in B:
			D=B[ATTR_FLASH]
			if D==FLASH_SHORT:C=.5
			else:C=2.
			await A.flash_binary(C);return
		A._state=_B;A._attr_brightness=255;A._channel.set_fade(A.get_target_values(),0);A.async_schedule_update_ha_state()
	async def flash_binary(A,duration):A._state=not A._state;A._attr_brightness=255 if A._state else 0;A._channel.set_fade(A.get_target_values(),0);await asyncio.sleep(duration);A._state=not A._state;A._attr_brightness=255 if A._state else 0;A._channel.set_fade(A.get_target_values(),0)
	async def async_turn_off(A,**B):A._state=_E;A._attr_brightness=0;A._channel.set_fade(A.get_target_values(),0);A.async_schedule_update_ha_state()
	async def restore_state(A,old_state):
		B=old_state;log.debug('Added binary light to hass. Try restoring state.');A._state=B.state;A._attr_brightness=B.attributes.get(_C)
		if B.state==STATE_ON:await A.async_turn_on()
		else:await A.async_turn_off()
class DmxDimmer(DmxBaseLight):
	CONF_TYPE=_I
	def __init__(A,**B):super().__init__(**B);A._channel_width=1;A._features=LightEntityFeature.TRANSITION|LightEntityFeature.FLASH;A._color_mode=ColorMode.BRIGHTNESS;A._supported_color_modes.add(ColorMode.BRIGHTNESS);A._channel_setup=B.get(CONF_CHANNEL_SETUP)or'd';validate(A._channel_setup,A.CONF_TYPE)
	def _update_values(B,values):B._state,B._attr_brightness,A,A,A,A,A,A,A,A=from_values(B._channel_setup,B.channel_size[1],values);B._channel_value_change()
	def get_target_values(A):return to_values(A._channel_setup,A._channel_size[1],A.is_on,A._attr_brightness)
	async def async_turn_on(B,**A):
		if ATTR_BRIGHTNESS in A:B._attr_brightness=A[ATTR_BRIGHTNESS]
		await super().async_create_fade(**A)
	async def restore_state(B,old_state):
		A=old_state;log.debug('Added dimmer to hass. Try restoring state.')
		if A:C=A.attributes.get(_C);B._attr_brightness=C
		if A.state!=STATE_OFF:await super().async_create_fade(brightness=B._attr_brightness,transition=0)
class DmxWhite(DmxBaseLight):
	CONF_TYPE='color_temp'
	def __init__(A,**B):super().__init__(**B);A._features=LightEntityFeature.TRANSITION|LightEntityFeature.FLASH;A._color_mode=ColorMode.COLOR_TEMP;A._supported_color_modes.add(ColorMode.COLOR_TEMP);A._min_kelvin=convert_to_kelvin(B[CONF_DEVICE_MIN_TEMP]);A._max_kelvin=convert_to_kelvin(B[CONF_DEVICE_MAX_TEMP]);A._vals=int((A._max_kelvin+A._min_kelvin)/2);A._channel_setup=B.get(CONF_CHANNEL_SETUP)or'ch';validate(A._channel_setup,A.CONF_TYPE);A._channel_width=len(A._channel_setup)
	@property
	def color_temp_kelvin(self):return self._vals
	@property
	def min_color_temp_kelvin(self):return self._min_kelvin
	@property
	def max_color_temp_kelvin(self):return self._max_kelvin
	def _update_values(A,values):A._state,A._attr_brightness,B,B,B,B,B,C,B,B=from_values(A._channel_setup,A.channel_size[1],values,A._min_kelvin,A._max_kelvin);A._vals=C;A._channel_value_change()
	def get_target_values(A):return to_values(A._channel_setup,A._channel_size[1],A.is_on,A._attr_brightness,color_temp_kelvin=A.color_temp_kelvin,min_kelvin=A.min_color_temp_kelvin,max_kelvin=A.max_color_temp_kelvin)
	async def async_turn_on(B,**A):
		C=B._vals;D=B._attr_brightness
		if ATTR_COLOR_TEMP_KELVIN in A:B._vals=A[ATTR_COLOR_TEMP_KELVIN]
		elif ATTR_WHITE in A:B._vals=(B._max_kelvin+B._min_kelvin)/2;B._attr_brightness=A[ATTR_WHITE]
		if ATTR_BRIGHTNESS in A:B._attr_brightness=A[ATTR_BRIGHTNESS]
		if ATTR_FLASH in A:await super().flash(C,D,**A)
		else:await super().async_create_fade(**A)
	async def restore_state(A,old_state):
		B=old_state;log.debug('Added color_temp to hass. Try restoring state.')
		if B:C=B.attributes.get(_D);A._vals=C;D=B.attributes.get(_C);A._attr_brightness=D
		if B.state!=STATE_OFF:await super().async_create_fade(brightness=A._attr_brightness,rgb_color=A._vals,transition=0)
class DmxRGB(DmxBaseLight):
	CONF_TYPE='rgb'
	def __init__(A,**B):super().__init__(**B);A._features=LightEntityFeature.TRANSITION|LightEntityFeature.FLASH;A._color_mode=ColorMode.RGB;A._supported_color_modes.add(ColorMode.RGB);A._supported_color_modes.add(ColorMode.HS);A._vals=255,255,255;A._channel_setup=B.get(CONF_CHANNEL_SETUP)or'rgb';validate(A._channel_setup,A.CONF_TYPE);A._channel_width=len(A._channel_setup);A._auto_scale_white='w'in A._channel_setup or'W'in A._channel_setup
	@property
	def rgb_color(self):return self._vals
	def _update_values(A,values):A._state,A._attr_brightness,C,D,E,B,B,B,B,B=from_values(A._channel_setup,A.channel_size[1],values);A._vals=C,D,E;A._channel_value_change()
	def get_target_values(A):
		B=A._vals[0];C=A._vals[1];D=A._vals[2]
		if A._auto_scale_white:B,C,D,E=color_rgb_to_rgbw(B,C,D)
		else:E=-1
		return to_values(A._channel_setup,A._channel_size[1],A.is_on,A._attr_brightness,B,C,D,E)
	async def async_turn_on(B,**A):
		C=B._vals;D=B._attr_brightness
		if ATTR_RGB_COLOR in A:B._vals=A[ATTR_RGB_COLOR]
		if ATTR_HS_COLOR in A:E,F=A[ATTR_HS_COLOR];B._vals=color_util.color_hs_to_RGB(E,F)
		if ATTR_BRIGHTNESS in A:B._attr_brightness=A[ATTR_BRIGHTNESS]
		if ATTR_FLASH in A:await super().flash(C,D,**A)
		else:await super().async_create_fade(**A)
	async def restore_state(A,old_state):
		B=old_state;log.debug('Added rgb to hass. Try restoring state.')
		if B:C=B.attributes.get(_D);A._vals=C;D=B.attributes.get(_C);A._attr_brightness=D
		if B.state!=STATE_OFF:await super().async_create_fade(brightness=A._attr_brightness,rgb_color=A._vals,transition=0)
class DmxRGBW(DmxBaseLight):
	CONF_TYPE='rgbw'
	def __init__(A,**B):super().__init__(**B);A._features=LightEntityFeature.TRANSITION|LightEntityFeature.FLASH;A._color_mode=ColorMode.RGBW;A._supported_color_modes.add(ColorMode.RGBW);A._supported_color_modes.add(ColorMode.HS);A._vals=[255,255,255,255];A._channel_setup=B.get(CONF_CHANNEL_SETUP)or'rgbw';validate(A._channel_setup,A.CONF_TYPE);A._channel_width=len(A._channel_setup)
	@property
	def rgbw_color(self):return tuple(self._vals)
	def _update_values(A,values):A._state,A._attr_brightness,C,D,E,F,B,B,B,B=from_values(A._channel_setup,A.channel_size[1],values);A._vals=[C,D,E,F];A._channel_value_change()
	def get_target_values(A):B=A._vals[0];C=A._vals[1];D=A._vals[2];E=A._vals[3];return to_values(A._channel_setup,A._channel_size[1],A.is_on,A._attr_brightness,B,C,D,E)
	async def async_turn_on(B,**A):
		C=list(B._vals);D=B._attr_brightness
		if ATTR_RGBW_COLOR in A:B._vals=list(A[ATTR_RGBW_COLOR])
		if ATTR_HS_COLOR in A:E,F=A[ATTR_HS_COLOR];B._vals[0:3]=list(color_util.color_hs_to_RGB(E,F))
		if ATTR_BRIGHTNESS in A:B._attr_brightness=A[ATTR_BRIGHTNESS]
		if ATTR_FLASH in A:await super().flash(C,D,**A)
		else:await super().async_create_fade(**A)
	async def restore_state(A,old_state):
		B=old_state;log.debug('Added rgbw to hass. Try restoring state.')
		if B:C=B.attributes.get(_D);A._vals=C;D=B.attributes.get(_C);A._attr_brightness=D
		if B.state!=STATE_OFF:await super().async_create_fade(brightness=A._attr_brightness,rgbw_color=A._vals,transition=0)
class DmxRGBWW(DmxBaseLight):
	CONF_TYPE='rgbww'
	def __init__(A,**B):super().__init__(**B);A._features=LightEntityFeature.TRANSITION|LightEntityFeature.FLASH;A._color_mode=ColorMode.RGBWW;A._supported_color_modes.add(ColorMode.RGBWW);A._supported_color_modes.add(ColorMode.COLOR_TEMP);A._supported_color_modes.add(ColorMode.HS);A._min_kelvin=convert_to_kelvin(B[CONF_DEVICE_MIN_TEMP]);A._max_kelvin=convert_to_kelvin(B[CONF_DEVICE_MAX_TEMP]);A._vals=[255,255,255,255,255,(A._max_kelvin-A._min_kelvin)/2];A._channel_setup=B.get(CONF_CHANNEL_SETUP)or'rgbch';validate(A._channel_setup,A.CONF_TYPE);A._channel_width=len(A._channel_setup)
	def _update_values(A,values):A._state,A._attr_brightness,B,C,D,E,F,G,H,H=from_values(A._channel_setup,A.channel_size[1],values);A._vals=B,C,D,E,F,G;A._channel_value_change()
	@property
	def rgbww_color(self):return tuple(self._vals[0:5])
	@property
	def min_color_temp_kelvin(self):return self._min_kelvin
	@property
	def max_color_temp_kelvin(self):return self._max_kelvin
	@property
	def color_temp_kelvin(self):return self._vals[5]
	def get_target_values(A):B=A._vals[0];C=A._vals[1];D=A._vals[2];E=A._vals[3];F=A._vals[4];G=A._vals[5];return to_values(A._channel_setup,A._channel_size[1],A.is_on,A._attr_brightness,B,C,D,E,F,color_temp_kelvin=G,min_kelvin=A.min_color_temp_kelvin,max_kelvin=A.max_color_temp_kelvin)
	async def async_turn_on(A,**B):
		C=list(A._vals);E=A._attr_brightness
		if ATTR_RGBWW_COLOR in B:
			A._vals[0:5]=B[ATTR_RGBWW_COLOR]
			if A._vals[3]!=C[3]or A._vals[4]!=C[4]:A._vals[5],D=color_util.rgbww_to_color_temperature((A._vals[0],A._vals[1],A._vals[2],A._vals[3],A._vals[4]),A.min_color_temp_kelvin,A.max_color_temp_kelvin);A._channel_value_change()
		if ATTR_HS_COLOR in B:F,G=B[ATTR_HS_COLOR];A._vals[0:3]=list(color_util.color_hs_to_RGB(F,G))
		if ATTR_BRIGHTNESS in B:A._attr_brightness=B[ATTR_BRIGHTNESS]
		if ATTR_COLOR_TEMP_KELVIN in B:A._vals[5]=B[ATTR_COLOR_TEMP_KELVIN];D,D,D,A._vals[3],A._vals[4]=color_util.color_temperature_to_rgbww(A._vals[5],A._attr_brightness,A.min_color_temp_kelvin,A.max_color_temp_kelvin);A._channel_value_change()
		if ATTR_FLASH in B:await super().flash(C,E,**B)
		else:await super().async_create_fade(**B)
	async def restore_state(A,old_state):
		B=old_state;log.debug('Added rgbww to hass. Try restoring state.')
		if B:
			C=B.attributes.get(_D)
			if len(C)==6:A._vals=C
			D=B.attributes.get(_C);A._attr_brightness=D
		if B.state!=STATE_OFF:await super().async_create_fade(brightness=A._attr_brightness,rgbww_color=A._vals,transition=0)
class DmxXY(DmxBaseLight):
	CONF_TYPE='xy'
	def __init__(A,**B):super().__init__(**B);A._features=LightEntityFeature.TRANSITION|LightEntityFeature.FLASH;A._color_mode=ColorMode.XY;A._supported_color_modes.add(ColorMode.XY);A._vals=[.0,.0];A._channel_setup=B.get(CONF_CHANNEL_SETUP)or'dxy';validate(A._channel_setup,A.CONF_TYPE);A._channel_width=len(A._channel_setup)
	def _update_values(A,values):
		A._state,A._attr_brightness,B,B,B,B,B,B,D,E=from_values(A._channel_setup,A.channel_size[1],values)
		def C(value):return value/255.
		A._vals=C(D),C(E);A._channel_value_change()
	@property
	def xy_color(self):return tuple(self._vals[0:2])
	def get_target_values(A):B=A._vals[0];C=A._vals[1];log.debug('get_target_values: x=%s, y=%s, brightness=%s, channel_size=%s',B,C,A._attr_brightness,A._channel_size[1]);return to_values(A._channel_setup,A._channel_size[1],A.is_on,A._attr_brightness,x=B,y=C)
	async def async_turn_on(B,**A):
		C=list(B._vals);D=B._attr_brightness
		if ATTR_XY_COLOR in A:
			log.debug(A);B._vals=A[ATTR_XY_COLOR]
			if B._vals[0]!=C[0]or B._vals[1]!=C[1]:B._channel_value_change()
		if ATTR_BRIGHTNESS in A:B._attr_brightness=A[ATTR_BRIGHTNESS]
		if ATTR_FLASH in A:await super().flash(C,D,**A)
		else:await super().async_create_fade(**A)
	async def restore_state(A,old_state):
		B=old_state;log.debug('Added xy to hass. Try restoring state.')
		if B:
			C=B.attributes.get(_D)
			if len(C)==2:A._vals=C
			D=B.attributes.get(_C);A._attr_brightness=D
		if B.state!=STATE_OFF:await super().async_create_fade(brightness=A._attr_brightness,xy_color=A._vals,transition=0)
__CLASS_LIST=[DmxDimmer,DmxRGB,DmxWhite,DmxRGBW,DmxRGBWW,DmxBinary,DmxFixed,DmxXY]
__CLASS_TYPE={A.CONF_TYPE:A for A in __CLASS_LIST}
PLATFORM_SCHEMA=PLATFORM_SCHEMA.extend({vol.Required(CONF_NODE_HOST):cv.string,vol.Required(CONF_NODE_UNIVERSES):{vol.All(int,vol.Range(min=0,max=1024)):{vol.Optional(CONF_SEND_PARTIAL_UNIVERSE,default=_B):cv.boolean,vol.Optional(CONF_OUTPUT_CORRECTION,default=_F):vol.Any(_A,vol.In(AVAILABLE_CORRECTIONS)),CONF_DEVICES:vol.All(cv.ensure_list,[{vol.Required(CONF_DEVICE_CHANNEL):vol.All(vol.Coerce(int),vol.Range(min=1,max=512)),vol.Required(CONF_DEVICE_NAME):cv.string,vol.Optional(CONF_DEVICE_FRIENDLY_NAME):cv.string,vol.Optional(CONF_DEVICE_TYPE,default=_I):vol.In([A.CONF_TYPE for A in __CLASS_LIST]),vol.Optional(CONF_DEVICE_TRANSITION,default=0):vol.All(vol.Coerce(float),vol.Range(min=0,max=999)),vol.Optional(CONF_OUTPUT_CORRECTION,default=_A):vol.Any(_A,vol.In(AVAILABLE_CORRECTIONS)),vol.Optional(CONF_CHANNEL_SIZE,default='8bit'):vol.Any(_A,vol.In(CHANNEL_SIZE)),vol.Optional(CONF_BYTE_ORDER,default='big'):vol.Any(_A,vol.In(['little','big'])),vol.Optional(CONF_DEVICE_MIN_TEMP,default='2700K'):vol.Match(_J),vol.Optional(CONF_DEVICE_MAX_TEMP,default='6500K'):vol.Match(_J),vol.Optional(CONF_CHANNEL_SETUP,default=_A):vol.Any(_A,cv.string,cv.ensure_list)}])}},vol.Optional(CONF_NODE_HOST_OVERRIDE,default=''):cv.string,vol.Optional(CONF_NODE_PORT):cv.port,vol.Optional(CONF_NODE_PORT_OVERRIDE):cv.port,vol.Optional(CONF_NODE_MAX_FPS,default=25):vol.All(vol.Coerce(int),vol.Range(min=1,max=50)),vol.Optional(CONF_NODE_REFRESH,default=120):vol.All(vol.Coerce(float),vol.Range(min=0,max=9999)),vol.Optional(CONF_NODE_TYPE,default=_G):vol.Any(_A,vol.In([_G,_H,'sacn','kinet']))},required=_B,extra=vol.PREVENT_EXTRA)