from __future__ import annotations
_I='remove_fixture'
_H='license'
_G='manual'
_F='universe'
_E='add_fixture'
_D='node_settings'
_C='title'
_B='host'
_A=None
import logging
from typing import Any
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry,ConfigFlow,ConfigFlowResult,OptionsFlow
from homeassistant.core import callback
from.import discovery
from.const import BYTE_ORDERS,CHANNEL_SIZES,CONF_HOST,DEFAULT_NODE,DEVICE_TYPES,DOMAIN,NODE_TYPES,OPT_DEV_BYTE_ORDER,OPT_DEV_CHANNEL,OPT_DEV_CHANNEL_SETUP,OPT_DEV_CHANNEL_SIZE,OPT_DEV_MAX_TEMP,OPT_DEV_MIN_TEMP,OPT_DEV_NAME,OPT_DEV_OUTPUT_CORRECTION,OPT_DEV_TRANSITION,OPT_DEV_TYPE,OPT_MAX_FPS,OPT_NODE,OPT_NODE_TYPE,OPT_PORT,OPT_REFRESH_EVERY,OPT_UNI_DEVICES,OPT_UNI_NAME,OPT_UNI_OUTPUT_CORRECTION,OPT_UNI_SEND_PARTIAL,OPT_UNIVERSES,OUTPUT_CORRECTIONS
from.models import OptionsValidationError,apply_device_defaults,default_options,validate_options
_LOGGER=logging.getLogger(__name__)
NONE_CORRECTION='none'
class ArtNetConfigFlow(ConfigFlow,domain=DOMAIN):
	VERSION=1
	def __init__(A):A._discovered=[]
	async def async_step_user(A,user_input=_A):return A.async_show_menu(step_id='user',menu_options=['scan',_G])
	async def async_step_manual(A,user_input=_A):
		B=user_input;D={}
		if B is not _A:C=B[CONF_HOST].strip();await A.async_set_unique_id(C);A._abort_if_unique_id_configured();E=B.get(_C,'').strip()or f"Art-Net {C}";return A.async_create_entry(title=E,data={CONF_HOST:C},options=default_options())
		F=vol.Schema({vol.Required(CONF_HOST):str,vol.Optional(_C,default=''):str});return A.async_show_form(step_id=_G,data_schema=F,errors=D)
	async def async_step_controller(A,user_input=_A):await A.async_set_unique_id('controller');A._abort_if_unique_id_configured();return A.async_create_entry(title='Art-Net Controller',data={'_controller':True})
	async def async_step_scan(A,user_input=_A):
		C=user_input
		if C is not _A:B=C[CONF_HOST];E=next((A for A in A._discovered if A[_B]==B),_A);F=(E or{}).get(_C)or f"Art-Net {B}";await A.async_set_unique_id(B);A._abort_if_unique_id_configured();return A.async_create_entry(title=F,data={CONF_HOST:B},options=default_options())
		A._discovered=await discovery.async_discover();G={A.data.get(CONF_HOST)for A in A._async_current_entries()};D={A[_B]:f"{A[_C]} ({A[_B]})"for A in A._discovered if A[_B]not in G}
		if not D:return A.async_abort(reason='no_nodes_found')
		H=vol.Schema({vol.Required(CONF_HOST):vol.In(D)});return A.async_show_form(step_id='scan',data_schema=H)
	async def async_step_integration_discovery(A,discovery_info):B=discovery_info;C=B[CONF_HOST];await A.async_set_unique_id(C);A._abort_if_unique_id_configured();A._discovered=[B];A.context['title_placeholders']={_B:C};return await A.async_step_discovery_confirm()
	async def async_step_discovery_confirm(A,user_input=_A):
		C=A._discovered[0]if A._discovered else{};B=C.get(CONF_HOST)or A.unique_id
		if user_input is not _A:D=C.get(_C)or f"Art-Net {B}";return A.async_create_entry(title=D,data={CONF_HOST:B},options=default_options())
		return A.async_show_form(step_id='discovery_confirm',description_placeholders={_B:B})
	@staticmethod
	@callback
	def async_get_options_flow(config_entry):return ArtNetOptionsFlow()
def _correction_choices():return{NONE_CORRECTION:'none',**{A:A for A in OUTPUT_CORRECTIONS}}
class ArtNetOptionsFlow(OptionsFlow):
	def _options(A):import copy;return copy.deepcopy(dict(A.config_entry.options)or default_options())
	async def async_step_init(A,user_input=_A):return A.async_show_menu(step_id='init',menu_options=[_H,_D,_E,_I])
	async def async_step_license(A,user_input=_A):
		C=user_input;B='license_key';D=A._options()
		if C is not _A:D[B]=C.get(B,'').strip();return A.async_create_entry(title='',data=D)
		E=vol.Schema({vol.Required(B,default=A.config_entry.options.get(B,'')):str});return A.async_show_form(step_id=_H,data_schema=E)
	async def async_step_node_settings(A,user_input=_A):
		B=user_input;C=A._options();D={**DEFAULT_NODE,**C.get(OPT_NODE,{})}
		if B is not _A:
			D.update({OPT_PORT:int(B[OPT_PORT]),OPT_NODE_TYPE:B[OPT_NODE_TYPE],OPT_MAX_FPS:int(B[OPT_MAX_FPS]),OPT_REFRESH_EVERY:float(B[OPT_REFRESH_EVERY])});C[OPT_NODE]=D
			try:validate_options(C)
			except OptionsValidationError as E:return A.async_show_form(step_id=_D,data_schema=A._node_schema(D),errors={'base':E.error_key})
			return A.async_create_entry(title='',data=C)
		return A.async_show_form(step_id=_D,data_schema=A._node_schema(D))
	@staticmethod
	def _node_schema(node):A=node;return vol.Schema({vol.Required(OPT_PORT,default=A[OPT_PORT]):vol.All(vol.Coerce(int),vol.Range(min=1,max=65535)),vol.Required(OPT_NODE_TYPE,default=A[OPT_NODE_TYPE]):vol.In(NODE_TYPES),vol.Required(OPT_MAX_FPS,default=A[OPT_MAX_FPS]):vol.All(vol.Coerce(int),vol.Range(min=1,max=50)),vol.Required(OPT_REFRESH_EVERY,default=A[OPT_REFRESH_EVERY]):vol.All(vol.Coerce(float),vol.Range(min=0,max=9999))})
	async def async_step_add_fixture(B,user_input=_A):
		A=user_input;C=B._options()
		if A is not _A:
			E=str(int(A[_F]));D=A[OPT_DEV_OUTPUT_CORRECTION];F=apply_device_defaults({OPT_DEV_CHANNEL:int(A[OPT_DEV_CHANNEL]),OPT_DEV_NAME:A[OPT_DEV_NAME].strip(),OPT_DEV_TYPE:A[OPT_DEV_TYPE],OPT_DEV_CHANNEL_SIZE:A[OPT_DEV_CHANNEL_SIZE],OPT_DEV_BYTE_ORDER:A[OPT_DEV_BYTE_ORDER],OPT_DEV_TRANSITION:float(A[OPT_DEV_TRANSITION]),OPT_DEV_OUTPUT_CORRECTION:_A if D==NONE_CORRECTION else D,OPT_DEV_MIN_TEMP:A[OPT_DEV_MIN_TEMP],OPT_DEV_MAX_TEMP:A[OPT_DEV_MAX_TEMP],OPT_DEV_CHANNEL_SETUP:A.get(OPT_DEV_CHANNEL_SETUP)or _A});G=C.setdefault(OPT_UNIVERSES,{});H=G.setdefault(E,{OPT_UNI_NAME:'',OPT_UNI_OUTPUT_CORRECTION:'linear',OPT_UNI_SEND_PARTIAL:True,OPT_UNI_DEVICES:[]});H.setdefault(OPT_UNI_DEVICES,[]).append(F)
			try:validate_options(C)
			except OptionsValidationError as I:return B.async_show_form(step_id=_E,data_schema=B._fixture_schema(A),errors={'base':I.error_key})
			return B.async_create_entry(title='',data=C)
		return B.async_show_form(step_id=_E,data_schema=B._fixture_schema())
	@staticmethod
	def _fixture_schema(prev=_A):A=prev;A=A or{};return vol.Schema({vol.Required(_F,default=A.get(_F,0)):vol.All(vol.Coerce(int),vol.Range(min=0,max=32767)),vol.Required(OPT_DEV_CHANNEL,default=A.get(OPT_DEV_CHANNEL,1)):vol.All(vol.Coerce(int),vol.Range(min=1,max=512)),vol.Required(OPT_DEV_NAME,default=A.get(OPT_DEV_NAME,'')):str,vol.Required(OPT_DEV_TYPE,default=A.get(OPT_DEV_TYPE,'dimmer')):vol.In(DEVICE_TYPES),vol.Required(OPT_DEV_CHANNEL_SIZE,default=A.get(OPT_DEV_CHANNEL_SIZE,'8bit')):vol.In(CHANNEL_SIZES),vol.Required(OPT_DEV_BYTE_ORDER,default=A.get(OPT_DEV_BYTE_ORDER,'big')):vol.In(BYTE_ORDERS),vol.Required(OPT_DEV_TRANSITION,default=A.get(OPT_DEV_TRANSITION,0)):vol.All(vol.Coerce(float),vol.Range(min=0,max=999)),vol.Required(OPT_DEV_OUTPUT_CORRECTION,default=A.get(OPT_DEV_OUTPUT_CORRECTION,NONE_CORRECTION)):vol.In(_correction_choices()),vol.Optional(OPT_DEV_CHANNEL_SETUP,default=A.get(OPT_DEV_CHANNEL_SETUP,'')or''):str,vol.Required(OPT_DEV_MIN_TEMP,default=A.get(OPT_DEV_MIN_TEMP,'2700K')):str,vol.Required(OPT_DEV_MAX_TEMP,default=A.get(OPT_DEV_MAX_TEMP,'6500K')):str})
	async def async_step_remove_fixture(A,user_input=_A):
		I='fixture';E=user_input;F=A._options();G=F.get(OPT_UNIVERSES,{})or{};B={}
		for(C,J)in G.items():
			for(D,H)in enumerate(J.get(OPT_UNI_DEVICES,[])or[]):K=f"U{C} · ch{H.get(OPT_DEV_CHANNEL)} · {H.get(OPT_DEV_NAME)}";B[K]=C,D
		if not B:return A.async_abort(reason='no_fixtures')
		if E is not _A:C,D=B[E[I]];del G[C][OPT_UNI_DEVICES][D];return A.async_create_entry(title='',data=F)
		L=vol.Schema({vol.Required(I):vol.In(list(B))});return A.async_show_form(step_id=_I,data_schema=L)