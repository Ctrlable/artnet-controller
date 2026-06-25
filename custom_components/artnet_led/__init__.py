from __future__ import annotations
_F='_panel_config'
_E='_controller'
_D='_sidebar_show'
_C=None
_B=True
_A=False
import logging,time
from pathlib import Path
from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant,callback
from homeassistant.helpers.instance_id import async_get as async_get_instance_id
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration
from.import websocket_api
from.license import LicenseError,check_revocation_online,load_license_cache,periodic_revocation_check,save_license_cache,validate_license_offline
from.const import DOMAIN,PANEL_ELEMENT,PANEL_FOLDER,PANEL_ICON,PANEL_JS,PANEL_STATIC_URL,PANEL_TITLE,PANEL_URL_PATH
_LOGGER=logging.getLogger(__name__)
PLATFORMS=[Platform.LIGHT]
async def async_setup(hass,config):A=hass;B=A.data.setdefault(DOMAIN,{});websocket_api.async_register(A);C=Path(__file__).parent/PANEL_FOLDER;await A.http.async_register_static_paths([StaticPathConfig(PANEL_STATIC_URL,str(C),_A)]);D=await async_get_integration(A,DOMAIN);E=f"{PANEL_STATIC_URL}/{PANEL_JS}?v={D.version}";B[_F]={'_panel_custom':{'name':PANEL_ELEMENT,'embed_iframe':_A,'trust_external':_A,'module_url':E}};B[_D]=await _load_sidebar_show(A);_update_sidebar_panel(A);return _B
_SIDEBAR_STORE_KEY='artnet_led_sidebar'
async def _load_sidebar_show(hass):from homeassistant.helpers.storage import Store;A=Store(hass,1,_SIDEBAR_STORE_KEY);B=await A.async_load()or{};return bool(B.get('show',_A))
async def _save_sidebar_show(hass,show):from homeassistant.helpers.storage import Store;A=Store(hass,1,_SIDEBAR_STORE_KEY);await A.async_save({'show':bool(show)})
@callback
def async_set_sidebar(hass,show):hass.data.setdefault(DOMAIN,{})[_D]=bool(show);_update_sidebar_panel(hass)
@callback
def _update_sidebar_panel(hass):
	F='_sidebar_shown';D='_panel_registered';C=hass;A=C.data.setdefault(DOMAIN,{});E=A.get(_F)
	if E is _C:return
	B=bool(A.get(_D))
	if A.get(D)and A.get(F)==B:return
	if A.get(D):
		try:frontend.async_remove_panel(C,PANEL_URL_PATH)
		except Exception:pass
	try:frontend.async_register_built_in_panel(C,component_name='custom',sidebar_title=PANEL_TITLE if B else _C,sidebar_icon=PANEL_ICON if B else _C,frontend_url_path=PANEL_URL_PATH,require_admin=_B,config=E);A[D]=_B;A[F]=B
	except Exception as G:_LOGGER.warning('Could not register Art-Net panel: %s',G)
@callback
def _async_ensure_controller_entry(hass):
	A=hass
	if any(A.data.get(_E)for A in A.config_entries.async_entries(DOMAIN)):return
	A.async_create_task(A.config_entries.flow.async_init(DOMAIN,context={'source':'controller'},data={}))
async def _async_setup_controller_entry(hass,entry):await hass.config_entries.async_forward_entry_setups(entry,[Platform.SWITCH]);return _B
async def async_setup_entry(hass,entry):
	C=entry;A=hass
	if C.data.get(_E):return await _async_setup_controller_entry(A,C)
	_async_ensure_controller_entry(A);E=(C.options.get('license_key')or'').strip()
	if not E:_LOGGER.error("Ctrlable Art-Net: no license key configured. Open the integration's Configure dialog and paste your license key.");return _A
	J=await async_get_integration(A,DOMAIN);K=str(J.version)
	try:B=validate_license_offline(E,current_version=K)
	except LicenseError as L:_LOGGER.error('Ctrlable Art-Net: license validation failed — %s',L);return _A
	if B.warn_only:_LOGGER.warning('Ctrlable Art-Net: license has expired but warn_only mode is active. Please renew your license.')
	D=await async_get_instance_id(A)
	if B.binding=='instance'and B.instance_id and B.instance_id!=D:_LOGGER.error('Ctrlable Art-Net: license is bound to instance %s; this HA is %s.',B.instance_id,D);return _A
	F=await check_revocation_online(B.jti,instance_id=D)
	if F is _A:_LOGGER.error('Ctrlable Art-Net: license rejected by portal. Aborting setup.');return _A
	G=await load_license_cache(A);H=G.get('last_ok')if G.get('jti')==B.jti else _C
	if F is _B:await save_license_cache(A,B.jti)
	elif H is not _C:
		I=(time.time()-H)/86400
		if I>30:_LOGGER.warning('Ctrlable Art-Net: portal unreachable for %.0f days. Ensure this device can reach portal.ctrlable.com periodically.',I)
	await A.config_entries.async_forward_entry_setups(C,PLATFORMS);C.async_on_unload(C.add_update_listener(_async_update_listener));A.async_create_background_task(periodic_revocation_check(A,B.jti,C.entry_id,instance_id=D),name=f"artnet_led_license_check_{C.entry_id}");return _B
async def async_unload_entry(hass,entry):
	A=entry
	if A.data.get(_E):return await hass.config_entries.async_unload_platforms(A,[Platform.SWITCH])
	return await hass.config_entries.async_unload_platforms(A,PLATFORMS)
async def _async_update_listener(hass,entry):await hass.config_entries.async_reload(entry.entry_id)