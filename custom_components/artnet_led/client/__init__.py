_D=None
_C='Protocol is not 14!'
_B=True
_A=False
import datetime,logging,re
from dataclasses import dataclass,field
from enum import Enum
from typing import Optional
CLIENT_VERSION=1
PROTOCOL_VERSION=14
PORT=6454
HOME_ASSISTANT_ESTA=ord('H')<<8+ord('A')
log=logging.getLogger(__name__)
class OpCode(Enum):OP_POLL=8192;OP_POLL_REPLY=8448;OP_DIAG_DATA=8960;OP_COMMAND=9216;OP_OUTPUT_DMX=20480;OP_NZS=20736;OP_SYNC=20992;OP_ADDRESS=24576;OP_INPUT=28672;OP_TOD_REQUEST=32768;OP_TOD_DATA=33024;OP_TOD_CONTROL=33280;OP_RDM=33536;OP_RDM_SUB=33792;OP_VIDEO_SETUP=40976;OP_VIDEO_PALETTE=40992;OP_VIDEO_DATA=41024;OP_MAC_MASTER=61440;OP_MAC_SLAVE=61696;OP_FIRMWARE_MASTER=61952;OP_FIRMWARE_REPLY=62208;OP_FILE_TN_MASTER=62464;OP_FILE_FN_MASTER=62720;OP_FILE_FN_REPLY=62976;OP_IP_PROG=63488;OP_IP_PROG_REPLY=63744;OP_MEDIA=36864;OP_MEDIA_PATCH=37120;OP_MEDIA_CONTROL=37376;OP_MEDIA_CONTROL_REPLY=37632;OP_TIME_CODE=38656;OP_TIME_SYNC=38912;OP_TRIGGER=39168;OP_DIRECTORY=39424;OP_DIRECTORY_REPLY=39680
class DiagnosticsMode(Enum):UNICAST=_A;BROADCAST=_B
class DiagnosticsPriority(Enum):DP_UNKNOWN=0;DP_LOW=16;DP_MED=64;DP_HIGH=128;DP_CRITICAL=224;DP_VOLATILE=240
class NodeReport(Enum):
	RC_DEBUG=0;RC_POWER_OK=1;RC_POWER_FAIL=2;RC_SOCKET_WR1=3;RC_PARSE_FAIL=4;RC_UDP_FAIL=5;RC_SH_NAME_OK=6;RC_LO_NAME_OK=7;RC_DMX_ERROR=8;RC_DMX_UDP_FULL=9;RC_DMX_RX_FULL=10;RC_SWITCH_ERR=11;RC_CONFIG_ERR=12;RC_DMX_SHORT=13;RC_FIRMWARE_FAIL=14;RC_USER_FAIL=15;RC_FACTORY_RES=16
	def report(A,reply_count,status_message):return f"#{hex(A.value)[2:]} [{str(reply_count).zfill(4)}] {status_message}"
class StyleCode(Enum):ST_NODE=0,'A DMX to / from Art-Net device';ST_CONTROLLER=1,'A lighting console.';ST_MEDIA=2,'A Media Server.';ST_ROUTE=3,'A network routing device.';ST_BACKUP=4,'A backup device.';ST_CONFIG=5,'A configuration or diagnostic tool.';ST_VISUAL=6,'A visualiser.'
@dataclass(order=_B)
class PortAddress:
	net:int=0;sub_net:int=0;universe:int=0
	def __init__(A,net,sub_net,universe=0):super().__init__();A.net=net;A.sub_net=sub_net;A.universe=universe
	@property
	def port_address(self):A=self;return A.net<<13|A.sub_net<<9|A.universe
	@port_address.setter
	def port_address(self,port_address):B=port_address;A=self;A.net=B>>13&15;A.sub_net=B>>9&15;A.universe=B&511
	@staticmethod
	def parse(port_address):A=port_address;return PortAddress(A>>13&15,A>>9&15,A&511)
	def __str__(A):return f"{A.net}:{A.sub_net}:{A.universe}"
	def __hash__(A):return A.port_address
class IndicatorState(Enum):UNKNOWN=0;LOCATE_IDENTIFY=1;MUTE_MODE=2;NORMAL_MODE=3
class PortAddressProgrammingAuthority(Enum):UNKNOWN=0;FRONT_PANEL=1;PROGRAMMATIC=2
class BootProcess(Enum):FLASH=_A;ROM=_B
class PortType(Enum):DMX512=0;MIDI=1;AVAB=2;COLORTRAN_CMX=3;ADB_65_2=4;ART_NET=5;DALI=6
@dataclass
class GoodInput:
	data_received:bool=_A;includes_dmx512_test_packets:bool=_A;includes_dmx512_sips:bool=_A;includes_dmx512_text_packets:bool=_A;input_disabled:bool=_A;receive_errors_detected:bool=_A
	@property
	def flags(self):A=self;return(A.data_received<<7)+(A.includes_dmx512_test_packets<<6)+(A.includes_dmx512_sips<<5)+(A.includes_dmx512_text_packets<<4)+(A.input_disabled<<3)+(A.receive_errors_detected<<2)
	@flags.setter
	def flags(self,flags):B=flags;A=self;A.data_received=bool(B>>7&1);A.includes_dmx512_test_packets=bool(B>>6&1);A.includes_dmx512_sips=bool(B>>5&1);A.includes_dmx512_text_packets=bool(B>>4&1);A.input_disabled=bool(B>>3&1);A.receive_errors_detected=bool(B>>2&1)
@dataclass
class GoodOutputA:
	data_being_transmitted:bool=_A;includes_dmx512_test_packets:bool=_A;includes_dmx512_sips:bool=_A;includes_dmx512_text_packets:bool=_A;merging_enabled:bool=_A;short_detected:bool=_A;merge_is_ltp:bool=_A;use_sacn:bool=_A
	@property
	def flags(self):A=self;return(A.data_being_transmitted<<7)+(A.includes_dmx512_test_packets<<6)+(A.includes_dmx512_sips<<5)+(A.includes_dmx512_text_packets<<4)+(A.merging_enabled<<3)+(A.short_detected<<2)+(A.merge_is_ltp<<1)+A.use_sacn
	@flags.setter
	def flags(self,flags):B=flags;A=self;A.data_being_transmitted=bool(B>>7&1);A.includes_dmx512_test_packets=bool(B>>6&1);A.includes_dmx512_sips=bool(B>>5&1);A.includes_dmx512_text_packets=bool(B>>4&1);A.merging_enabled=bool(B>>3&1);A.short_detected=bool(B>>2&1);A.merge_is_ltp=bool(B>>1&1);A.use_sacn=bool(B&1)
@dataclass
class Port:
	input:bool=_A;output:bool=_A;type:PortType=PortType.DMX512;good_input:GoodInput=field(default_factory=GoodInput);good_output_a:GoodOutputA=field(default_factory=GoodOutputA);sw_in:int=0;sw_out:int=0;rdm_enabled:bool=_A;output_continuous:bool=_B;last_input_seen:datetime=datetime.datetime.now()
	@property
	def port_types_flags(self):A=self;return(A.output<<7)+(A.input<<6)+A.type.value
	@port_types_flags.setter
	def port_types_flags(self,flags):B=flags;A=self;A.output=bool(B>>7&1);A.input=bool(B>>6&1);A.type=PortType(B&63)
	@property
	def good_output_b(self):return(self.rdm_enabled<<7)+(self.output_continuous<<6)
	@good_output_b.setter
	def good_output_b(self,flags):A=flags;self.rdm_enabled=bool(A>>7&1);self.output_continuous=bool(A>>6&1)
class FailsafeState(Enum):HOLD_LAST_STATE=0;ALL_OUTPUTS_0=1;ALL_OUTPUTS_FULL=2;PLAYBACK_FAIL_SAFE_SCENE=3
@dataclass
class ArtIpProgCommand:
	enable_programming:bool=_A;enable_dhcp:bool=_A;program_default_gateway:bool=_A;set_parameters_to_default:bool=_A;program_ip_address:bool=_A;program_subnet_mask:bool=_A;program_port:bool=_A
	@property
	def flags(self):A=self;return(A.enable_programming<<7)+(A.enable_dhcp<<6)+(A.program_default_gateway<<4)+(A.set_parameters_to_default<<3)+(A.program_ip_address<<2)+(A.program_subnet_mask<<1)+A.program_port
	@flags.setter
	def flags(self,flags):B=flags;A=self;A.enable_programming=bool(B>>7&1);A.enable_dhcp=bool(B>>6&1);A.program_default_gateway=bool(B>>4&1);A.set_parameters_to_default=bool(B>>3&1);A.program_ip_address=bool(B>>2&1);A.program_subnet_mask=bool(B>>1&1);A.program_port=bool(B&1)
class ArtAddressCommand(Enum):
	AC_NONE=0;AC_CANCEL_MERGE=1;AC_LED_NORMAL=2;AC_LED_MUTE=3;AC_LED_LOCATE=4;AC_RESET_RX_FLAGS=5;AC_ANALYSIS_ON=6;AC_ANALYSIS_OFF=7;AC_FAIL_HOLD=8;AC_FAIL_ZERO=9;AC_FAIL_FULL=10;AC_FAIL_SCENE=11;AC_FAIL_RECORD=12;AC_MERGE_LTP=16;AC_DIRECTION_TX=32;AC_DIRECTION_RX=48;AC_MERGE_HTP=80;AC_ART_NET_SEL=96;AC_ACN_SEL=112;AC_CLEAR_OP=144;AC_STYLE_DELTA=160;AC_STYLE_CONST=176;AC_RDM_ENABLE=192;AC_RDM_DISABLE=208
	def apply_port_index(A,port_index):return A.value if A.value>=16 else A.value+port_index
	@staticmethod
	def decode_with_port_index(value):
		A=value
		if A>=16:B=A&15;A-=B
		else:B=0
		return ArtAddressCommand(A),B
class ValueAction(Enum):RESET=0;IGNORE=1;WRITE=2
class TimeCodeType(Enum):FILM=0;EBU=1;DF=2;SMPTE=3
class ArtBase:
	__ENCODINGS__=['utf8','iso-8859-1']
	def __init__(A,opcode):super().__init__();A.__opcode=opcode
	def serialize(B):A=bytearray();A.extend(map(ord,'Art-Net\x00'));B._append_int_lsb(A,B.__opcode.value);return A
	def deserialize(A,packet):
		C=packet;D,B=A._consume_str(C,0,8)
		if D!='Art-Net':raise SerializationException(f'Not a valid packet, expected "Art-Net", but is "{D}"')
		E,B=A._consume_int_lsb(C,B)
		if E!=A.__opcode.value:raise SerializationException(f"Expected this packet to have opcode {A.__opcode}, but was {E}")
		return B
	@staticmethod
	def _pop(packet,index):A=index;return packet[A],A+1
	@staticmethod
	def _take(packet,n,index):A=index;return packet[A:A+n],A+n
	@staticmethod
	def _append_int_lsb(packet,number):B=number;A=packet;A.append(B&255);A.append(B>>8&255)
	@staticmethod
	def _append_int_msb(packet,number):B=number;A=packet;A.append(B>>8&255);A.append(B&255)
	@staticmethod
	def _consume_int_lsb(packet,index):
		B=packet;A=index
		if len(B)<A+2:raise SerializationException(f"Not enough bytes in packet: {bytes(B).hex()}")
		[C,D]=B[A:A+2];return D<<8|C,A+2
	@staticmethod
	def _consume_int_msb(packet,index):
		B=packet;A=index
		if len(B)<A+2:raise SerializationException(f"Not enough bytes in packet: {bytes(B).hex()}")
		[C,D]=B[A:A+2];return C<<8|D,A+2
	@staticmethod
	def _consume_hex_number_lsb(packet,index):
		B=index;A=packet
		if len(A)<B+2:raise SerializationException(f"Not enough bytes in packet: {bytes(A).hex()}")
		C=hex(A[B])[2:].zfill(2);D=hex(A[B+1])[2:].zfill(2);return int(D+C,16),B+2
	@staticmethod
	def _consume_hex_number_msb(packet,index):
		B=index;A=packet
		if len(A)<B+2:raise SerializationException(f"Not enough bytes in packet: {bytes(A).hex()}")
		C=hex(A[B])[2:].zfill(2);D=hex(A[B+1])[2:].zfill(2);return int(C+D,16),B+2
	@staticmethod
	def _append_str(packet,text,length):A=length;B=text[:A-1];C=B.ljust(A,'\x00');packet.extend(map(ord,C))
	@staticmethod
	def _consume_str(packet,index,length):
		D=length;C=index;B=_D;A=packet[C:C+D]
		try:E=re.compile(b'([^\\x00]+)');F=E.match(A).group(1)if E.match(A)else A;G=re.sub(b'[^\x00-\x7f]',b'',F);B=G.decode('ascii')
		except UnicodeDecodeError:B=ArtBase._decode_bytes(A)
		if B is _D:log.error('Unable to convert bytes to string: {raw_hex}'.format(raw_hex=bytes(A).hex()))
		return B,C+D
	@staticmethod
	def _decode_bytes(byte_str):
		B=byte_str
		for A in ArtBase.__ENCODINGS__:
			try:D=B.decode(A);C=str(D).strip().strip('\x00');log.debug(f"decoded as {A}: {C}");return C
			except UnicodeDecodeError as E:log.warning(f"failed ({E.reason}) to decode as {A}: {bytes(B).hex()}")
	@staticmethod
	def peek_opcode(packet):
		A=packet
		if len(A)<9:return
		B=A[0:8]
		if B!=b'Art-Net\x00':return
		C=ArtBase._consume_int_lsb(A,8);return OpCode(C[0])
class ArtPoll(ArtBase):
	def __init__(A,protocol_version=PROTOCOL_VERSION,enable_vlc_transmission=_A,notify_on_change=_A):super().__init__(OpCode.OP_POLL);A.__protocol_version=protocol_version;A.__enable_vlc_transmission=enable_vlc_transmission;A.notify_on_change=notify_on_change;A.__enable_diagnostics=_A;A.__diag_priority=DiagnosticsPriority.DP_LOW;A.__diag_mode=DiagnosticsMode.BROADCAST;A.__enable_targeted_mode=_A;A.__target_port_bottom=PortAddress(0,0,0);A.__target_port_top=PortAddress(15,15,409)
	def enable_diagnostics(A,mode=DiagnosticsMode.BROADCAST,diag_priority=DiagnosticsPriority.DP_LOW):A.__enable_diagnostics=_B;A.__diag_priority=diag_priority;A.__diag_mode=mode
	@property
	def protocol_verison(self):return self.__protocol_version
	@property
	def vlc_transmission_enabled(self):return self.__enable_vlc_transmission
	@property
	def is_diagnostics_enabled(self):return self.__enable_diagnostics
	@property
	def diagnostics_priority(self):return self.__diag_priority
	@property
	def diagnostics_mode(self):return self.__diag_mode
	@property
	def targeted_mode_enabled(self):return self.__enable_targeted_mode
	@property
	def target_port_bounds(self):return self.__target_port_bottom,self.__target_port_top
	@target_port_bounds.setter
	def target_port_bounds(self,bounds):B=bounds;A=self;A.__target_port_bottom=B[0];A.__target_port_top=B[0];A.__enable_targeted_mode=_B
	def serialize(A):B=super().serialize();A._append_int_msb(B,A.__protocol_version);C=(A.__enable_targeted_mode<<5)+(A.__enable_vlc_transmission<<4)+(A.__diag_mode.value<<3)+(A.__enable_diagnostics<<2)+(A.notify_on_change<<1);B.append(C);B.append(A.__diag_priority.value);A._append_int_msb(B,A.__target_port_top.port_address);A._append_int_msb(B,A.__target_port_bottom.port_address);return B
	def deserialize(A,packet):
		C=packet;B=0
		try:B=super().deserialize(C);A.__protocol_version,B=A._consume_int_msb(C,B);D,B=A._pop(C,B);A.__enable_targeted_mode=bool(D>>5&1);A.__enable_vlc_transmission=bool(D>>4&1);A.__diag_mode=DiagnosticsMode(bool(D>>3&1));A.__enable_diagnostics=bool(D>>2&1);A.notify_on_change=bool(D>>1&1);A.__diag_priority=DiagnosticsPriority(C[B]);B+=1;A.__target_port_top.port_address,B=A._consume_int_msb(C,B);A.__target_port_bottom.port_address,B=A._consume_int_msb(C,B)
		except SerializationException as E:print(E)
		return B
class ArtPollReply(ArtBase):
	def __init__(A,source_ip=bytes([0]*4),firmware_version=0,net_switch=0,sub_switch=0,oem=0,indicator_state=IndicatorState.UNKNOWN,port_address_programming_authority=PortAddressProgrammingAuthority.UNKNOWN,boot_process=BootProcess.ROM,supports_rdm=_A,esta=HOME_ASSISTANT_ESTA,short_name='PyArtNet',long_name='Default long name',node_report='',ports=[],acn_priority=100,sw_macro_bitmap=0,sw_remote_bitmap=0,style=StyleCode.ST_CONTROLLER,mac_address=bytes([0]*6),bind_ip=bytes([0]*4),bind_index=1,supports_web_browser_configuration=_A,dhcp_configured=_A,dhcp_capable=_A,supports_15_bit_port_address=_B,supports_switching_to_sacn=_A,squawking=_A,supports_switching_of_output_style=_A,supports_rdm_through_artnet=_A,failsafe_state=FailsafeState.HOLD_LAST_STATE,supports_failover=_A,supports_switching_port_direction=_A):
		B=ports;super().__init__(opcode=OpCode.OP_POLL_REPLY);A.source_ip=source_ip;A.port=PORT;A.firmware_version=firmware_version;A.net_switch=net_switch;A.sub_switch=sub_switch;A.oem=oem;A.indicator_state=indicator_state;A.port_address_programming_authority=port_address_programming_authority;A.boot_process=boot_process;A.supports_rdm=supports_rdm;A.esta=esta;A.short_name=short_name;A.long_name=long_name;A.node_report=node_report;A.ports=B
		for C in range(4-len(B)):A.ports.append(Port())
		A.acn_priority=acn_priority;A.sw_macro_bitmap=sw_macro_bitmap;A.sw_remote_bitmap=sw_remote_bitmap;A.style=style;A.mac_address=mac_address;A.bind_ip=bind_ip;A.bind_index=bind_index;A.supports_web_browser_configuration=supports_web_browser_configuration;A.dhcp_configured=dhcp_configured;A.dhcp_capable=dhcp_capable;A.supports_15_bit_port_address=supports_15_bit_port_address;A.supports_switching_to_sacn=supports_switching_to_sacn;A.squawking=squawking;A.supports_switching_of_output_style=supports_switching_of_output_style;A.supports_rdm_through_artnet=supports_rdm_through_artnet;A.failsafe_state=failsafe_state;A.supports_failover=supports_failover;A.supports_switching_port_direction=supports_switching_port_direction;A.__ubea_present=_A;A.__ubea=0;A.__supports_llrp=_B;A.__default_resp_uid=[0]*6
	@property
	def ubea(self):return self.__ubea if self.__ubea_present else _D
	@ubea.setter
	def ubea(self,ubea):self.__ubea_present=_B;self.__ubea=ubea
	@property
	def default_resp_uid(self):return self.__default_resp_uid if self.__supports_llrp else _D
	@default_resp_uid.setter
	def default_resp_uid(self,default_resp_uid):self.__supports_llrp=_B;self.__default_resp_uid=default_resp_uid
	def serialize(A):B=super().serialize();B.extend(A.source_ip);C=hex(A.port)[2:];B.extend([int(C[2:4],16),int(C[0:2],16)]);A._append_int_msb(B,A.firmware_version);B.append(A.net_switch);B.append(A.sub_switch);A._append_int_msb(B,A.oem);B.append(A.ubea or 0);D=(A.indicator_state.value<<6)+(A.port_address_programming_authority.value<<4)+(A.boot_process.value<<2)+(A.supports_rdm<1)+A.__ubea_present;B.append(D);A._append_int_lsb(B,A.esta);A._append_str(B,A.short_name,18);A._append_str(B,A.long_name,64);A._append_str(B,A.node_report,64);A._append_int_msb(B,len([A for A in A.ports if A.input or A.output]));B.extend([A.port_types_flags for A in A.ports]);B.extend([A.good_input.flags for A in A.ports]);B.extend([A.good_output_a.flags for A in A.ports]);B.extend([A.sw_in for A in A.ports]);B.extend([A.sw_out for A in A.ports]);B.append(A.acn_priority);B.append(A.sw_macro_bitmap);B.append(A.sw_remote_bitmap);B.extend([0,0,0]);B.append(A.style.value[0]);B.extend(A.mac_address);B.extend(A.bind_ip);B.append(A.bind_index);E=A.supports_web_browser_configuration+(A.dhcp_configured<<1)+(A.dhcp_capable<<2)+(A.supports_15_bit_port_address<<3)+(A.supports_switching_to_sacn<<4)+(A.squawking<<5)+(A.supports_switching_of_output_style<<6)+(A.supports_rdm_through_artnet<<7);B.append(E);B.extend(map(lambda p:p.good_output_b,A.ports));F=(A.failsafe_state.value<<6)+(A.supports_failover<<5)+(A.__supports_llrp<<4)+(A.supports_switching_port_direction<3);B.append(F);B.extend(A.default_resp_uid);B.extend([0]*15);return B
	def deserialize(A,packet):
		C=packet;B=0
		try:
			B=super().deserialize(C);A.source_ip,B=A._take(C,4,B);A.port,B=A._consume_hex_number_lsb(C,B);A.firmware_version,B=A._consume_hex_number_msb(C,B);A.net_switch,B=A._pop(C,B);A.sub_switch,B=A._pop(C,B);A.oem,B=A._consume_hex_number_msb(C,B);A.ubea,B=A._pop(C,B);G,B=A._pop(C,B);A.indicator_state=IndicatorState(G>>6&2);A.port_address_programming_authority=PortAddressProgrammingAuthority(G>>4&2);A.boot_process=BootProcess(bool(G>>2&1));A.supports_rdm=bool(G>>1&1);A.__ubea_present=bool(G&1);A.esta,B=A._consume_hex_number_lsb(C,B);A.short_name,B=A._consume_str(C,B,18);A.long_name,B=A._consume_str(C,B,64);A.node_report,B=A._consume_str(C,B,64);I,B=A._consume_int_msb(C,B);J,B=A._take(C,4,B);K,B=A._take(C,4,B);L,B=A._take(C,4,B);M,B=A._take(C,4,B);N,B=A._take(C,4,B);A.acn_priority,B=A._pop(C,B);A.sw_macro_bitmap,B=A._pop(C,B);A.sw_remote_bitmap,B=A._pop(C,B);B+=3;A.style,B=A._pop(C,B);A.mac_address,B=A._take(C,6,B);A.bind_ip,B=A._take(C,4,B);A.bind_index,B=A._pop(C,B);D,B=A._pop(C,B);A.supports_web_browser_configuration=bool(D&1);A.dhcp_configured=bool(D>>1&1);A.dhcp_capable=bool(D>>2&1);A.supports_15_bit_port_address=bool(D>>3&1);A.supports_switching_to_sacn=bool(D>>4&1);A.squawking=bool(D>>5&1);A.supports_switching_of_output_style=bool(D>>6&1);A.supports_rdm_through_artnet=bool(D>>7&1);O,B=A._take(C,4,B)
			for E in range(I):F=A.ports[E];F.port_types_flags=J[E];F.good_input.flags=K[E];F.good_output_a.flags=L[E];F.sw_in=M[E];F.sw_out=N[E];F.good_output_b=O[E]
			H,B=A._pop(C,B);A.failsafe_state=FailsafeState(H>>6);A.supports_failover=bool(H>>5&1);A.__supports_llrp=bool(H>>4&1);A.supports_switching_port_direction=bool(H>>3&1);A.default_resp_uid,B=A._take(C,6,B);B+=15
		except SerializationException as P:print(P)
		return B
class ArtIpProg(ArtBase):
	def __init__(A,protocol_version=PROTOCOL_VERSION,command=ArtIpProgCommand(),prog_ip=bytes([0]*4),prog_subnet=bytes([0]*4),prog_gateway=bytes([0]*4)):super().__init__(OpCode.OP_IP_PROG);A.protocol_version=protocol_version;A.command=command;A.prog_ip=prog_ip;A.prog_subnet=prog_subnet;A.prog_gateway=prog_gateway
	def serialize(B):A=super().serialize();B._append_int_msb(A,B.protocol_version);A.extend([0]*2);A.append(B.command.flags);A.append(0);A.extend(B.prog_ip);A.extend(B.prog_subnet);A.extend([0]*2);A.extend(B.prog_gateway);A.extend([0]*4);return A
	def deserialize(B,packet):
		C=packet;A=0
		try:
			A=super().deserialize(C);B.protocol_version,A=B._consume_int_msb(C,A)
			if B.protocol_version!=14:raise SerializationException(_C)
			A+=2;B.command.flags,A=B._pop(C,A);A+=1;B.prog_ip,A=B._take(C,4,A);B.prog_subnet,A=B._take(C,4,A);A+=2;B.prog_gateway,A=B._take(C,4,A);A+=4
		except SerializationException as D:print(D)
		return A
class ArtIpProgReply(ArtBase):
	def __init__(A,protocol_version=PROTOCOL_VERSION,prog_ip=bytes([0]*4),prog_subnet=bytes([0]*4),prog_gateway=bytes([0]*4),dhcp_enabled=_A):super().__init__(OpCode.OP_IP_PROG_REPLY);A.protocol_version=protocol_version;A.prog_ip=prog_ip;A.prog_subnet=prog_subnet;A.prog_gateway=prog_gateway;A.dhcp_enabled=dhcp_enabled
	def serialize(B):A=super().serialize();B._append_int_msb(A,B.protocol_version);A.extend([0]*4);A.extend(B.prog_ip);A.extend(B.prog_subnet);A.extend([0]*2);A.append(B.dhcp_enabled<<6);A.append(0);A.extend(B.prog_gateway);A.extend([0]*2);return A
	def deserialize(B,packet):
		C=packet;A=0
		try:
			A=super().deserialize(C);B.protocol_version,A=B._consume_int_msb(C,A)
			if B.protocol_version!=14:raise SerializationException(_C)
			A+=4;B.prog_ip,A=B._take(C,4,A);B.prog_subnet,A=B._take(C,4,A);A+=2;D,A=B._pop(C,A);B.dhcp_enabled=bool(D>>6&1);A+=1;B.prog_gateway,A=B._take(C,4,A);A+=2
		except SerializationException as E:print(E)
		return A
class ArtAddress(ArtBase):
	def __init__(A,protocol_version=PROTOCOL_VERSION,net_switch=1,net_action=ValueAction.IGNORE,sub_switch=1,sub_action=ValueAction.IGNORE,bind_index=1,short_name='',long_name='',sw_in=[1]*4,sw_in_actions=[ValueAction.IGNORE]*4,sw_out=[1]*4,sw_out_actions=[ValueAction.IGNORE]*4,acn_priority=255,command=ArtAddressCommand.AC_NONE,command_port_index=0):E=sw_out_actions;D=sw_out;C=sw_in_actions;B=sw_in;super().__init__(opcode=OpCode.OP_ADDRESS);A.protocol_version=protocol_version;A.net_switch=net_switch;A.net_action=net_action;A.sub_switch=sub_switch;A.sub_action=sub_action;A.bind_index=bind_index;A.short_name=short_name;A.long_name=long_name;A.sw_in=B+[1]*(4-len(B));A.sw_in_actions=C+[ValueAction.IGNORE]*(4-len(C));A.sw_out=D+[1]*(4-len(D));A.sw_out_actions=E+[ValueAction.IGNORE]*(4-len(E));A.acn_priority=acn_priority;A.command=command;A.command_port_index=command_port_index
	def serialize(A):B=super().serialize();A._append_int_msb(B,A.protocol_version);B.append(ArtAddress.__apply_value_action(A.net_action,A.net_switch));B.append(A.bind_index);A._append_str(B,A.short_name,18);A._append_str(B,A.long_name,64);A.__append_sw_in_out(B,A.sw_in,A.sw_in_actions);A.__append_sw_in_out(B,A.sw_out,A.sw_out_actions);B.append(ArtAddress.__apply_value_action(A.sub_action,A.sub_switch));B.append(A.acn_priority);B.append(A.command.apply_port_index(A.command_port_index));return B
	def deserialize(A,packet):
		C=packet;B=0
		try:
			B=super().deserialize(C);A.protocol_version,B=A._consume_int_msb(C,B)
			if A.protocol_version!=14:raise SerializationException(_C)
			A.net_switch,A.net_action,B=A.__consume_value_and_action(C,B);A.bind_index,B,A._pop(C,B);A.short_name=A._consume_str(C,B,18);A.long_name=A._consume_str(C,B,64);A.sw_in,A.sw_in_actions,B=A.__consume_sw_in_out(C,B);A.sw_out,A.sw_out_actions,B=A.__consume_sw_in_out(C,B);A.sub_switch,A.sub_action,B=A.__consume_value_and_action(C,B);A.acn_priority,B=A._pop(C,B);D,B=A._pop(C,B);A.command,A.command_port_index=ArtAddressCommand.decode_with_port_index(D)
		except SerializationException as E:print(E)
		return B
	@staticmethod
	def __apply_value_action(action,value):
		A=action
		if A==ValueAction.RESET:return 0
		else:return(A==ValueAction.WRITE)<<7|value
	@staticmethod
	def __consume_value_and_action(packet,index):
		C=index;A=packet[C]
		if A==0:B=ValueAction.RESET
		elif A>>7&1:B=ValueAction.WRITE
		else:B=ValueAction.IGNORE
		return A,B,C+1
	@staticmethod
	def __append_sw_in_out(packet,sw,sw_actions):
		for A in range(4):packet.append(ArtAddress.__apply_value_action(sw_actions[A],sw[A]))
	@staticmethod
	def __consume_sw_in_out(packet,index):A=index;B=list(map(lambda i:ArtAddress.__consume_value_and_action(packet,A+i),range(4)));C=list(map(lambda sw_a:sw_a[0],B));D=list(map(lambda sw_a:sw_a[1],B));return C,D,A+4
class ArtDiagData(ArtBase):
	def __init__(A,protocol_version=PROTOCOL_VERSION,diag_priority=DiagnosticsPriority,logical_port=0,text=''):super().__init__(opcode=OpCode.OP_DIAG_DATA);A.protocol_version=protocol_version;A.diag_priority=diag_priority;A.logical_port=logical_port;A.text=text
	def serialize(A):B=super().serialize();A._append_int_msb(B,A.protocol_version);B.append(0);B.append(A.diag_priority.value);B.append(A.logical_port);B.append(0);A._append_int_msb(B,len(A.text));A._append_str(B,A.text,len(A.text)+1);return B
	def deserialize(B,packet):
		C=packet;A=0
		try:
			A=super().deserialize(C);B.protocol_version,A=B._consume_int_msb(C,A)
			if B.protocol_version!=14:raise SerializationException(_C)
			A+=1;D,A=B._pop(C,A);B.diag_priority=DiagnosticsPriority(D);B.logical_port,A=B._pop(C,A);A+=1;E,A=B._consume_int_msb(C,A);B.text,A=B._consume_str(C,A,E+1)
		except SerializationException as F:print(F)
		return A
class ArtTimeCode(ArtBase):
	def __init__(A,protocol_version=PROTOCOL_VERSION,frames=0,seconds=0,minutes=0,hours=0,type=TimeCodeType.FILM):super().__init__(opcode=OpCode.OP_TIME_CODE);A.protocol_version=protocol_version;A.frames=frames;A.seconds=seconds;A.minutes=minutes;A.hours=hours;A.type=type
	def serialize(B):A=super().serialize();B._append_int_msb(A,B.protocol_version);A.extend([0]*2);A.append(B.frames);A.append(B.seconds);A.append(B.minutes);A.append(B.hours);A.append(B.type.value);return A
	def deserialize(B,packet):
		C=packet;A=0
		try:
			A=super().deserialize(C);B.protocol_version,A=B._consume_int_msb(C,A)
			if B.protocol_version!=14:raise SerializationException(_C)
			A+=2;B.frames,A=B._pop(C,A);B.seconds,A=B._pop(C,A);B.minutes,A=B._pop(C,A);B.hours,A=B._pop(C,A);D,A=B._pop(C,A);B.type=TimeCodeType(D)
		except SerializationException as E:print(E)
		return A
class ArtCommand(ArtBase):
	def __init__(A,protocol_version=PROTOCOL_VERSION,esta=65535,command=''):super().__init__(opcode=OpCode.OP_COMMAND);A.protocol_version=protocol_version;A.esta=esta;A.command=command
	def serialize(A):B=super().serialize();A._append_int_msb(B,A.protocol_version);A._append_int_msb(B,A.esta);A._append_str(B,A.command,512);return B
	def deserialize(B,packet):
		C=packet;A=0
		try:
			A=super().deserialize(C);B.protocol_version,A=B._consume_int_msb(C,A)
			if B.protocol_version!=14:raise SerializationException(_C)
			B.esta,A=B._consume_int_msb(C,A);B.command,A=B._consume_str(C,A,512)
		except SerializationException as D:print(D)
		return A
class ArtTrigger(ArtBase):
	def __init__(A,protocol_version=PROTOCOL_VERSION,oem=65535,key=0,sub_key=0,payload=[0]*512):super().__init__(opcode=OpCode.OP_TRIGGER);A.protocol_version=protocol_version;A.oem=oem;A.key=key;A.sub_key=sub_key;A.payload=payload
	def serialize(A):B=super().serialize();A._append_int_msb(B,A.protocol_version);B.extend([0]*2);A._append_int_msb(B,A.oem);B.append(A.key);B.append(A.sub_key);B.extend(A.payload);return B
	def deserialize(A,packet):
		C=packet;B=0
		try:
			B=super().deserialize(C);A.protocol_version,B=A._consume_int_msb(C,B);B+=2;A.oem,B=A._consume_hex_number_msb(C,B)
			if A.protocol_version!=14:raise SerializationException(_C)
			A.key,B=A._pop(C,B);A.sub_key,B=A._pop(C,B)
			if A.oem==65535 and A.key>3:print(f"Warning: Trigger key range undefined for OEM '{A.oem}', key '{A.key}'")
			A.payload,B=A._take(C,B,512)
		except SerializationException as D:print(D)
		return B
class ArtDmx(ArtBase):
	def __init__(A,protocol_version=PROTOCOL_VERSION,sequence_number=0,physical=0,port_address=PortAddress(0,0,0),data=[0]*2):super().__init__(opcode=OpCode.OP_OUTPUT_DMX),;A.protocol_version=protocol_version;A.sequence_number=sequence_number;A.physical=physical;A.port_address=port_address;A.data=data
	def serialize(A):B=super().serialize();A._append_int_msb(B,A.protocol_version);B.append(A.sequence_number);B.append(A.physical);C=A.port_address.port_address;B.append(C&15);B.append(C>>8&15);A._append_int_msb(B,len(A.data));B.extend(A.data);return B
	def deserialize(B,packet):
		C=packet;A=0
		try:A=super().deserialize(C);B.protocol_version,A=B._consume_int_msb(C,A);B.sequence_number,A=B._pop(C,A);B.physical,A=B._pop(C,A);D,A=B._pop(C,A);E,A=B._pop(C,A);B.port_address.port_address=E<<8|D;F,A=B._consume_int_msb(C,A);B.data,A=B._take(C,F,A)
		except SerializationException as G:print(G)
		return A
class SerializationException(Exception):
	def __init__(B,*A):super().__init__(*A)