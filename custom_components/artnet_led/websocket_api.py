from __future__ import annotations
_V='dmx_set_failed'
_U='Node is not running'
_T='not_sending'
_S='loaded'
_R='runtime_data'
_Q='source'
_P='fixtures'
_O='channel'
_N='name'
_M='options'
_L='license_key'
_K='profile'
_J='profiles'
_I='title'
_H='value'
_G='universe'
_F=True
_E='host'
_D='entry_id'
_C='type'
_B=None
_A='id'
import asyncio,logging
from typing import Any
from uuid import uuid4
import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.config_entries import SOURCE_INTEGRATION_DISCOVERY,ConfigEntryState
from homeassistant.core import HomeAssistant,callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.instance_id import async_get as async_get_instance_id
from homeassistant.helpers.storage import Store
from homeassistant.loader import async_get_integration
from.import discovery
from.const import CONF_HOST,DEVICE_TYPES,DOMAIN
from.license import LicenseError,load_license_cache,validate_license_offline
from.models import OptionsValidationError,count_fixtures,validate_options
_LOGGER=logging.getLogger(__name__)
PROFILES_STORE_KEY='artnet_led_profiles'
PROFILES_STORE_VERSION=1
@callback
def async_register(hass):A=hass;websocket_api.async_register_command(A,ws_list_entries);websocket_api.async_register_command(A,ws_get_config);websocket_api.async_register_command(A,ws_save_config);websocket_api.async_register_command(A,ws_scan);websocket_api.async_register_command(A,ws_create_entry);websocket_api.async_register_command(A,ws_list_profiles);websocket_api.async_register_command(A,ws_save_profile);websocket_api.async_register_command(A,ws_delete_profile);websocket_api.async_register_command(A,ws_node_status);websocket_api.async_register_command(A,ws_test_connection);websocket_api.async_register_command(A,ws_fixtures_state);websocket_api.async_register_command(A,ws_dmx_values);websocket_api.async_register_command(A,ws_dmx_set);websocket_api.async_register_command(A,ws_dmx_set_all);websocket_api.async_register_command(A,ws_license_status);websocket_api.async_register_command(A,ws_set_license)
def _profiles_store(hass):
	C='profiles_store';B=hass.data.setdefault(DOMAIN,{});A=B.get(C)
	if A is _B:A=Store(hass,PROFILES_STORE_VERSION,PROFILES_STORE_KEY);B[C]=A
	return A
async def _load_profiles(hass):A=await _profiles_store(hass).async_load();return list((A or{}).get(_J,[]))
def _entry_or_error(hass,connection,msg):
	A=hass.config_entries.async_get_entry(msg[_D])
	if A is _B or A.domain!=DOMAIN:connection.send_error(msg[_A],'not_found','Unknown Art-Net entry');return
	return A
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/list_entries'})
@callback
def ws_list_entries(hass,connection,msg):A=[{_D:A.entry_id,_I:A.title,_E:A.data.get(CONF_HOST)}for A in hass.config_entries.async_entries(DOMAIN)];connection.send_result(msg[_A],{'entries':A})
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/get_config',vol.Required(_D):str})
@callback
def ws_get_config(hass,connection,msg):
	B=connection;A=_entry_or_error(hass,B,msg)
	if A is _B:return
	B.send_result(msg[_A],{_E:A.data.get(CONF_HOST),_M:dict(A.options)})
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/save_config',vol.Required(_D):str,vol.Required(_M):dict})
@websocket_api.async_response
async def ws_save_config(hass,connection,msg):
	B=connection;A=msg;D=_entry_or_error(hass,B,A)
	if D is _B:return
	C=A[_M]
	try:validate_options(C)
	except OptionsValidationError as E:B.send_error(A[_A],E.error_key,str(E));return
	hass.config_entries.async_update_entry(D,options=C);B.send_result(A[_A],{_P:count_fixtures(C)})
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/scan'})
@websocket_api.async_response
async def ws_scan(hass,connection,msg):A=await discovery.async_discover();connection.send_result(msg[_A],{'nodes':A})
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/create_entry',vol.Required(_E):str,vol.Optional(_I):str})
@websocket_api.async_response
async def ws_create_entry(hass,connection,msg):
	D=connection;C=hass;A=msg;E=A[_E].strip()
	for F in C.config_entries.async_entries(DOMAIN):
		if F.data.get(CONF_HOST)==E:D.send_result(A[_A],{_D:F.entry_id});return
	G={CONF_HOST:E}
	if A.get(_I):G[_I]=A[_I]
	B=await C.config_entries.flow.async_init(DOMAIN,context={_Q:SOURCE_INTEGRATION_DISCOVERY},data=G)
	if B.get(_C)=='form':B=await C.config_entries.flow.async_configure(B['flow_id'],{})
	if B.get(_C)!='create_entry':D.send_error(A[_A],'create_failed',f"Could not create entry for {E}");return
	D.send_result(A[_A],{_D:B['result'].entry_id})
_PROFILE_FIELDS='manufacturer','model',_N,_C,'channel_setup','channel_size','byte_order','output_correction','min_temp','max_temp','note'
def _clean_profile(raw):
	B=raw;A={A:B[A]for A in _PROFILE_FIELDS if B.get(A)not in(_B,'')};A[_C]=B.get(_C,'dimmer')
	if A[_C]not in DEVICE_TYPES:raise OptionsValidationError('invalid_type',f"Unknown type {A[_C]!r}")
	if not(A.get('model')or A.get(_N)):raise OptionsValidationError('missing_name','Profile needs a model or name')
	return A
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/list_profiles'})
@websocket_api.async_response
async def ws_list_profiles(hass,connection,msg):connection.send_result(msg[_A],{_J:await _load_profiles(hass)})
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/save_profile',vol.Required(_K):dict})
@websocket_api.async_response
async def ws_save_profile(hass,connection,msg):
	D=connection;B=msg
	try:A=_clean_profile(B[_K])
	except OptionsValidationError as E:D.send_error(B[_A],E.error_key,str(E));return
	A[_Q]='user';A[_A]=B[_K].get(_A)or f"user_{uuid4().hex[:10]}";C=await _load_profiles(hass);C=[B for B in C if B.get(_A)!=A[_A]];C.append(A);await _profiles_store(hass).async_save({_J:C});D.send_result(B[_A],{_K:A})
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/delete_profile',vol.Required(_A):str})
@websocket_api.async_response
async def ws_delete_profile(hass,connection,msg):A=await _load_profiles(hass);B=[A for A in A if A.get(_A)!=msg[_A]];await _profiles_store(hass).async_save({_J:B});connection.send_result(msg[_A],{'ok':_F,'removed':len(A)-len(B)})
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/node_status',vol.Required(_D):str})
@callback
def ws_node_status(hass,connection,msg):
	B=connection;A=_entry_or_error(hass,B,msg)
	if A is _B:return
	C=getattr(A,_R,_B);B.send_result(msg[_A],{_S:A.state==ConfigEntryState.LOADED,'sending':C is not _B,_E:A.data.get(CONF_HOST)})
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/test_connection',vol.Required(_D):str})
@websocket_api.async_response
async def ws_test_connection(hass,connection,msg):
	B=msg;A=connection;C=_entry_or_error(hass,A,B)
	if C is _B:return
	F=C.data.get(CONF_HOST)
	try:D=await discovery.async_discover(timeout=2.5)
	except Exception as G:A.send_error(B[_A],'test_failed',str(G));return
	E=next((A for A in D if A.get(_E)==F),_B);A.send_result(B[_A],{'replied':E is not _B,'node':E,'responders':len(D)})
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/fixtures_state',vol.Required(_D):str})
@callback
def ws_fixtures_state(hass,connection,msg):
	K='unavailable';J='color_temp_kelvin';I='rgb_color';H='brightness';F=connection;D=msg;C=hass;L=_entry_or_error(C,F,D)
	if L is _B:return
	M=er.async_get(C);G=[]
	for B in er.async_entries_for_config_entry(M,D[_D]):A=C.states.get(B.entity_id);E=A.attributes if A else{};G.append({'entity_id':B.entity_id,'unique_id':B.unique_id,_N:(A.name if A else _B)or B.original_name,'state':A.state if A else K,'available':bool(A)and A.state not in(K,'unknown'),H:E.get(H),I:E.get(I),J:E.get(J)})
	F.send_result(D[_A],{_P:G})
DMX_SIZE=512
def _node_of(entry):return getattr(entry,_R,_B)
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/dmx_values',vol.Required(_D):str,vol.Required(_G):int})
@callback
def ws_dmx_values(hass,connection,msg):
	C=connection;B=msg;D=_entry_or_error(hass,C,B)
	if D is _B:return
	E=_node_of(D);A=[]
	if E is not _B:
		try:F=E.get_universe(int(B[_G]));A=list(bytes(F._data))[:DMX_SIZE]
		except Exception:A=[]
	if len(A)<DMX_SIZE:A+=[0]*(DMX_SIZE-len(A))
	C.send_result(B[_A],{'values':A})
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/dmx_set',vol.Required(_D):str,vol.Required(_G):int,vol.Required(_O):vol.All(int,vol.Range(min=1,max=DMX_SIZE)),vol.Required(_H):vol.All(int,vol.Range(min=0,max=255))})
@websocket_api.async_response
async def ws_dmx_set(hass,connection,msg):
	C=connection;A=msg;G=_entry_or_error(hass,C,A)
	if G is _B:return
	F=_node_of(G)
	if F is _B:C.send_error(A[_A],_T,_U);return
	H=int(A[_G]);D=int(A[_O]);I=int(A[_H])
	try:
		try:B=F.get_universe(H)
		except Exception:B=F.add_universe(H)
		try:B._resize_universe(DMX_SIZE)
		except Exception:pass
		E=B._data
		if len(E)<D:E.extend(bytes(D-len(E)))
		E[D-1]=I&255
		try:B._data_changed=_F
		except Exception:pass
		J=B.send_data()
		if asyncio.iscoroutine(J):await J
	except Exception as K:C.send_error(A[_A],_V,str(K));return
	C.send_result(A[_A],{'ok':_F,_O:D,_H:I})
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/dmx_set_all',vol.Required(_D):str,vol.Required(_G):int,vol.Required(_H):vol.All(int,vol.Range(min=0,max=255))})
@websocket_api.async_response
async def ws_dmx_set_all(hass,connection,msg):
	C=connection;A=msg;F=_entry_or_error(hass,C,A)
	if F is _B:return
	E=_node_of(F)
	if E is _B:C.send_error(A[_A],_T,_U);return
	G=int(A[_G]);H=int(A[_H])&255
	try:
		try:B=E.get_universe(G)
		except Exception:B=E.add_universe(G)
		try:B._resize_universe(DMX_SIZE)
		except Exception:pass
		D=B._data
		if len(D)<DMX_SIZE:D.extend(bytes(DMX_SIZE-len(D)))
		for J in range(DMX_SIZE):D[J]=H
		try:B._data_changed=_F
		except Exception:pass
		I=B.send_data()
		if asyncio.iscoroutine(I):await I
	except Exception as K:C.send_error(A[_A],_V,str(K));return
	C.send_result(A[_A],{'ok':_F,_H:H})
async def _license_status(hass,entry):
	H='jti';G='valid';E=entry;C=hass;I=await async_get_instance_id(C);D=(E.options.get(_L)or'').strip();B={'instance_id':I,'has_key':bool(D),_S:E.state==ConfigEntryState.LOADED}
	if not D:return B
	try:J=await async_get_integration(C,DOMAIN);A=validate_license_offline(D,current_version=str(J.version))
	except LicenseError as K:B.update({G:False,'error':str(K)});return B
	F=await load_license_cache(C);B.update({G:_F,H:A.jti,'product':A.product,'expires_at':A.expires_at,'binding':A.binding,'bound_instance':A.instance_id,'max_version':A.max_version,'on_expire':A.on_expire,'last_check':F.get('last_ok')if F.get(H)==A.jti else _B});return B
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/license_status',vol.Required(_D):str})
@websocket_api.async_response
async def ws_license_status(hass,connection,msg):
	A=connection;B=_entry_or_error(hass,A,msg)
	if B is _B:return
	A.send_result(msg[_A],await _license_status(hass,B))
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required(_C):'artnet_led/set_license',vol.Required(_D):str,vol.Required(_L):str})
@websocket_api.async_response
async def ws_set_license(hass,connection,msg):
	D=connection;C=msg;B=hass;A=_entry_or_error(B,D,C)
	if A is _B:return
	E={**A.options,_L:C[_L].strip()};B.config_entries.async_update_entry(A,options=E);await B.config_entries.async_reload(A.entry_id);A=B.config_entries.async_get_entry(C[_D]);D.send_result(C[_A],await _license_status(B,A))