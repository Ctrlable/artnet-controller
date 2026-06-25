from __future__ import annotations
_A=False
from typing import Any
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo,EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from.const import DOMAIN,PANEL_URL_PATH
async def async_setup_entry(hass,entry,async_add_entities):
	A=entry
	if A.data.get('_controller'):async_add_entities([ArtNetControllerSwitch(hass,A)])
class ArtNetControllerSwitch(SwitchEntity):
	_attr_has_entity_name=True;_attr_should_poll=_A;_attr_entity_category=EntityCategory.CONFIG;_attr_name='Show in sidebar';_attr_icon='mdi:dock-left'
	def __init__(A,hass,entry):B=entry;A._hass=hass;A._entry=B;A._attr_unique_id=f"{B.entry_id}_show_in_sidebar";A._attr_is_on=_A
	@property
	def device_info(self):A='Art-Net Controller';return DeviceInfo(identifiers={(DOMAIN,'controller')},name=A,manufacturer='Ctrlable',model=A,configuration_url=f"homeassistant://{PANEL_URL_PATH}")
	async def async_added_to_hass(A):await super().async_added_to_hass();from.import _load_sidebar_show as B,async_set_sidebar as C;A._attr_is_on=await B(A._hass);C(A._hass,A._attr_is_on);A.async_write_ha_state()
	async def async_turn_on(A,**B):await A._set(True)
	async def async_turn_off(A,**B):await A._set(_A)
	async def _set(A,show):B=show;from.import _save_sidebar_show as C,async_set_sidebar as D;A._attr_is_on=B;D(A._hass,B);await C(A._hass,B);A.async_write_ha_state()