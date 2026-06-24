_D='255.255.255.255'
_C=False
_B=True
_A=None
import asyncio,datetime,logging,random,uuid
from asyncio import transports,Task
from dataclasses import dataclass,field
from socket import socket
from typing import Any,Union
from _socket import SO_BROADCAST,AF_INET,SOCK_DGRAM,SOL_SOCKET,IPPROTO_UDP,inet_aton,inet_ntoa
from homeassistant.core import HomeAssistant
from netifaces import AF_INET
from custom_components.artnet_led.client import OpCode,ArtBase,ArtPoll,ArtPollReply,PortAddress,IndicatorState,PortAddressProgrammingAuthority,BootProcess,NodeReport,Port,PortType,StyleCode,FailsafeState,DiagnosticsMode,DiagnosticsPriority,ArtIpProgReply,ArtDiagData,ArtTimeCode,ArtCommand,ArtTrigger,ArtDmx
from custom_components.artnet_led.client.net_utils import get_private_ip,get_default_gateway
STALE_NODE_CUTOFF_TIME=10
ARTNET_PORT=6454
RDM_SUPPORT=_C
SWITCH_TO_SACN_SUPPORT=_C
ART_ADDRESS_SUPPORT=_C
HA_PHYSICAL_PORT=0
log=logging.getLogger(__name__)
@dataclass
class Node:
	addr:bytes=([0]*4,);bind_index:int=(0,);last_seen:datetime.datetime=(datetime.datetime.now(),);net_switch:int=(0,);sub_switch:int=0;ports:list[Port]=_A
	def get_addresses(A):
		if not A.ports:return set()
		B=set(map(lambda port:PortAddress(A.net_switch,A.sub_switch,port.sw_in),filter(lambda port:port.input,A.ports)));C=set(map(lambda port:PortAddress(A.net_switch,A.sub_switch,port.sw_out),filter(lambda port:port.output,A.ports)));return B.union(C)
	def __repr__(A):return str(A)
	def __str__(A):return f"{A.net_switch}:{A.sub_switch}:*@{inet_ntoa(A.addr)}#{A.bind_index}"
	def __eq__(A,other):B=other;return A.addr==B.addr and A.bind_index==B.bind_index
	def __hash__(A):return hash((A.addr,A.bind_index))
@dataclass
class OwnPort:port:Port=field(default_factory=Port);data:bytearray|_A=_A;update_task:Task[_A]=_A
class ArtNetServer(asyncio.DatagramProtocol):
	def __init__(A,hass,state_update_callback=_A,new_node_callback=_A,firmware_version=0,oem=0,esta=0,short_name='PyArtNet',long_name='Python ArtNet Server',is_server_dhcp_configured=_B,polling=_B,sequencing=_B,retransmit_time_ms=900):B=sequencing;super().__init__();A.__hass=hass;A.__state_update_callback=state_update_callback;A.__new_node_callback=new_node_callback;A.firmware_version=firmware_version;A.oem=oem;A.esta=esta;A.short_name=short_name;A.long_name=long_name;A.dhcp_configured=is_server_dhcp_configured;A._polling=polling;A._sequencing=B;A.sequence_number=1 if B else 0;A.retransmit_time_ms=retransmit_time_ms;A.own_port_addresses={};A.node_change_subscribers=set();A.nodes_by_ip={};A.nodes_by_port_address={};A._own_ip=inet_aton(get_private_ip());A._default_gateway=inet_aton(get_default_gateway());A.indicator_state=IndicatorState.LOCATE_IDENTIFY;A.node_report=NodeReport.RC_POWER_OK;A.status_message='Starting ArtNet server...';A.art_poll_reply_counter=0;A.swout_text='Output';A.swin_text='Input';A.startup_time=_A;A.mac=uuid.getnode().to_bytes(6,'big')
	def uptime(A):return(datetime.datetime.now()-A.startup_time).seconds if A.startup_time else 0
	def add_port(B,port_address):A=port_address;C=Port(input=_B,output=_B,type=PortType.ART_NET,sw_in=A.universe,sw_out=A.universe);B.own_port_addresses[A]=OwnPort(C);B.update_subscribers()
	def remove_port(A,port_address):del A.own_port_addresses[port_address];A.update_subscribers()
	def get_port_bounds(B):
		A=B.own_port_addresses.keys()
		if not A:return
		return min(A),max(A)
	def get_node_by_ip(A,addr,bind_index=1):return A.nodes_by_ip.get((addr,bind_index),_A)
	def add_node_by_ip(A,node,addr,bind_index=1):A.nodes_by_ip[addr,bind_index]=node
	def get_node_by_port_address(A,port_address):return A.nodes_by_port_address.get(port_address,_A)
	def add_node_by_port_address(A,port_address,node):
		C=node;B=port_address;D=A.nodes_by_port_address.get(B)
		if D:
			if C not in D:
				D.add(C)
				if A.uptime()>3:
					E=A.own_port_addresses.get(B,_A)
					if E and E.data:log.info(f"Since we have data on that node already, let's send an update immediately to it!");A.send_dmx(B,E.data)
		else:A.nodes_by_port_address[B]={C}
	def remove_node_by_ip(A,addr,bind_index=1):del A.nodes_by_ip[addr,bind_index]
	def remove_node_by_port_address(A,port_address,node):
		D=port_address;B=node;C=A.nodes_by_port_address[D]
		if not C:return
		if B in C:C.remove(B)
		if not C:del A.nodes_by_port_address[D]
		if B not in A.nodes_by_ip.values():
			E=inet_ntoa(B.addr)
			if E in A.node_change_subscribers:A.node_change_subscribers.remove(E)
	def update_subscribers(A):
		for B in A.node_change_subscribers:A.send_reply(B)
	def get_grouped_ports(B):
		D=set(map(lambda p:(p.net,p.sub_net),B.own_port_addresses));C=[[A[0],A[1],[B.universe for B in B.own_port_addresses if(B.net,B.sub_net)==A]]for A in D]
		for A in C:E=[A[2][B:B+4]for B in range(0,len(A[2]),4)];A[2]=[list(map(lambda u:B.own_port_addresses[PortAddress(A[0],A[1],u)].port,C))for C in E]
		return C
	def start_server(A):
		B=A.__hass.loop;C=B.create_datagram_endpoint(lambda:A,local_addr=('0.0.0.0',ARTNET_PORT))
		if A._polling:A.__hass.async_create_background_task(A.start_poll_loop(),'Art-Net polling loop')
		log.info('ArtNet server started');return A.__hass.async_create_task(C)
	async def start_poll_loop(B):
		while _B:
			A=ArtPoll();D=B.get_port_bounds()
			if D:
				A.target_port_bounds=D;A.notify_on_change=_B;A.enable_diagnostics(DiagnosticsMode.UNICAST,DiagnosticsPriority.DP_HIGH);log.debug('Sending ArtPoll')
				with socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)as C:C.setsockopt(SOL_SOCKET,SO_BROADCAST,1);C.setblocking(_C);C.sendto(A.serialize(),(_D,6454))
				B.__hass.async_create_background_task(B.remove_stale_nodes(),'Art-Net remove stale nodes');log.debug('Sleeping a few seconds before polling again...')
			await asyncio.sleep(random.uniform(2.5,3))
	async def remove_stale_nodes(D):
		await asyncio.sleep(STALE_NODE_CUTOFF_TIME);E=datetime.datetime.now();G=E-datetime.timedelta(seconds=STALE_NODE_CUTOFF_TIME);F=[]
		for((A,B),C)in D.nodes_by_ip.items():
			if C.last_seen>G:continue
			H=E-C.last_seen;log.warning(f"Haven't seen node {inet_ntoa(A)}#{B} for {H.seconds} seconds; removing it.");F+=[(A,B)]
			for I in C.get_addresses():D.remove_node_by_port_address(I,C)
		for(A,B)in F:del D.nodes_by_ip[A,B]
	@staticmethod
	def send_artnet(art_packet,ip):
		with socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)as A:A.setblocking(_C);A.sendto(art_packet.serialize(),(ip,ARTNET_PORT))
	def send_diagnostics(A,addr=_A,diagnostics_priority=DiagnosticsPriority.DP_MED,diagnostics_mode=DiagnosticsMode.BROADCAST):B=ArtDiagData(diag_priority=diagnostics_priority,logical_port=0,text=A.status_message);C=addr if diagnostics_mode==DiagnosticsMode.UNICAST else bytes(_D);A.send_artnet(B,C)
	def send_reply(A,addr):
		B=_A
		for(C,D,E)in A.get_grouped_ports():
			if B is _A:B=0 if len(E)==1 else 1
			for F in E:
				G=A.node_report.report(A.art_poll_reply_counter,A.status_message);H=ArtPollReply(source_ip=A._own_ip,firmware_version=A.firmware_version,net_switch=C,sub_switch=D,oem=A.oem,indicator_state=IndicatorState.LOCATE_IDENTIFY,port_address_programming_authority=PortAddressProgrammingAuthority.PROGRAMMATIC,boot_process=BootProcess.FLASH,supports_rdm=RDM_SUPPORT,esta=0,short_name=A.short_name,long_name=A.long_name,node_report=G,ports=F,style=StyleCode.ST_CONTROLLER,mac_address=A.mac,supports_web_browser_configuration=_B,dhcp_configured=A.dhcp_configured,dhcp_capable=_B,supports_15_bit_port_address=_B,supports_switching_to_sacn=SWITCH_TO_SACN_SUPPORT,squawking=RDM_SUPPORT,supports_switching_of_output_style=ART_ADDRESS_SUPPORT,bind_index=B,supports_rdm_through_artnet=RDM_SUPPORT,failsafe_state=FailsafeState.HOLD_LAST_STATE);log.debug(f"Sending ArtPollReply from bind_index {B} for {C}/{D}/[{",".join([str(A.sw_out)for A in F])}]");A.send_artnet(H,addr);A.art_poll_reply_counter+=1
				if B!=0:B+=1
	def send_dmx(A,address,data):
		C=address
		if not A.get_node_by_port_address(C):
			if A.uptime()<3:log.debug("Can't currently send DMX as nodes haven't had the chance to be discovered.");return
			if len(A.nodes_by_port_address)==0:log.error("The server hasn't received replies from any node at all. We don't know where we can send the DMX data to. If this message persists, consider using direct mode instead of the ArtNet server.")
			else:log.error(f"No nodes found that listen to port address {C}. Current nodes: {A.nodes_by_port_address.keys()}")
			return
		B=A.own_port_addresses[C]
		if B.update_task:B.update_task.cancel()
		E=B.port.good_output_a.data_being_transmitted
		if not E:B.port.good_output_a.data_being_transmitted=_B;A.update_subscribers()
		D=A.__hass.async_create_task(A.start_artdmx_loop(C,data,B));B.update_task=D;return D
	async def start_artdmx_loop(A,address,data,own_port):
		D=own_port;B=address;D.data=data;C=ArtDmx(sequence_number=A.sequence_number,physical=HA_PHYSICAL_PORT,port_address=B,data=data);E=C.serialize()
		while _B:
			F=A.get_node_by_port_address(B)
			if not F:log.warning(f"No nodes found that listen to port address {B}. Stopping sending ArtDmx refreshes...");D.port.good_output_a.data_being_transmitted=_C;A.update_subscribers()
			else:
				with socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)as G:
					G.setblocking(_C)
					for I in F:H=inet_ntoa(I.addr);log.debug(f"Sending ArtDmx to {H}");G.sendto(E,(H,ARTNET_PORT))
			if A._sequencing:
				A.sequence_number+=1
				if A.sequence_number>255:A.sequence_number=1
				C.sequence_number=A.sequence_number;E=C.serialize()
			if A.retransmit_time_ms==0:return
			await asyncio.sleep(A.retransmit_time_ms/1e3)
	def connection_made(A,transport):A.startup_time=datetime.datetime.now();log.debug('Server connection made');super().connection_made(transport)
	def connection_lost(A,exc):super().connection_lost(exc)
	def datagram_received(A,data,addr):A.handle_datagram(addr,data)
	def handle_datagram(E,addr,data):
		C=data;B=addr;C=bytearray(C);A=ArtBase.peek_opcode(C)
		if A==OpCode.OP_POLL:L=ArtPoll();L.deserialize(C);log.debug(f"Received ArtPoll from {B[0]}");E.handle_poll(B,L)
		elif A==OpCode.OP_POLL_REPLY:J=ArtPollReply();J.deserialize(C);log.debug(f"Received ArtPollReply from {J.long_name}");E.handle_poll_reply(B,J)
		elif A==OpCode.OP_IP_PROG:log.debug(f"Received IP prog request from {B[0]}, ignoring...")
		elif A==OpCode.OP_IP_PROG_REPLY:F=ArtIpProgReply();F.deserialize(C);log.debug(f"Received IP prog reply from {B[0]}:\n  IP      : {F.prog_ip}\n  Subnet  : {F.prog_subnet}\n  Gateway : {F.prog_gateway}\n  DHCP    : {F.dhcp_enabled}")
		elif A==OpCode.OP_ADDRESS:log.debug(f"Received Adress request from {B[0]}, not doing anything with it...")
		elif A==OpCode.OP_DIAG_DATA:H=ArtDiagData();H.deserialize(C);log.debug(f"Received Diag Data from {B[0]}:\n  Priority     : {H.diag_priority}\n  Logical port : {H.logical_port}\n  Text         : {H.text}")
		elif A==OpCode.OP_TIME_CODE:D=ArtTimeCode();D.deserialize(C);log.debug(f"Received Time Code from {B[0]}:\n  Current time/frame : {D.hours}:{D.minutes}:{D.seconds}.{D.frames}\n  Type               : {D.type}")
		elif A==OpCode.OP_COMMAND:I=ArtCommand();I.deserialize(C);log.debug(f"Received command from {B[0]}\n  ESTA    : {I.esta}\n  Command : {I.command}");E.handle_command(I)
		elif A==OpCode.OP_TRIGGER:G=ArtTrigger();G.deserialize(C);log.debug(f"Received trigger from {B[0]}\n  OEM    : {G.oem}\n  Key    : {G.key}\n  Subkey : {G.sub_key}");E.handle_trigger(G)
		elif A==OpCode.OP_OUTPUT_DMX:K=ArtDmx();K.deserialize(C);log.debug(f"Received DMX data from {B[0]}\n  Address: {K.port_address}");E.handle_dmx(K)
		elif A==OpCode.OP_SYNC:0
		else:log.warning(f"Received Opcode {A}, which isn't supported yet!")
	def should_handle_ports(B,lower_port,upper_port):
		if not B.own_port_addresses:return _C
		A=B.get_port_bounds()
		if not A:return _C
		return not(lower_port>A[1]or upper_port<A[0])
	def handle_poll_reply(B,addr,reply):
		A=reply
		if A.source_ip is not bytes([0]*4):D=inet_aton(inet_ntoa(A.source_ip))
		else:D=inet_aton(addr[0])
		if addr==B._own_ip:log.debug('Ignoring ArtPollReply as it came ourselves own address.');return
		if A.node_report:log.debug(f"  {A.node_report}")
		E=A.bind_index;C=B.get_node_by_ip(D,E);G=datetime.datetime.now()
		if not C:
			C=Node(D,E,G);B.add_node_by_ip(C,D,E);log.info(f"Discovered new node at {inet_ntoa(D)}@{E} with {A.net_switch}:{A.sub_switch}:[{",".join([str(A.sw_out)for A in A.ports if A.output])}]")
			if B.__new_node_callback:B.__new_node_callback(A)
		else:C.last_seen=G;log.debug(f"Existing node checking in {inet_ntoa(D)}@{E} with {A.net_switch}:{A.sub_switch}:[{",".join([str(A.sw_out)for A in A.ports])}]")
		H=C.get_addresses();C.net_switch=A.net_switch;C.sub_switch=A.sub_switch;C.ports=A.ports;F=C.get_addresses();log.debug(f"Addresses of the node at {inet_ntoa(D)}@{E}: {F}");I=H-F
		for J in I:B.remove_node_by_port_address(J,C)
		for K in F:
			B.add_node_by_port_address(K,C)
			if D!=B._own_ip:
				B.status_message='Discovered some ArtNet nodes!'
				if B.indicator_state==IndicatorState.LOCATE_IDENTIFY:B.indicator_state=IndicatorState.MUTE_MODE
	def handle_poll(A,addr,poll):
		C=addr;B=poll
		if inet_aton(C[0])==A._own_ip:log.debug('Ignoring ArtPoll as it came from ourselves');return
		if B.targeted_mode_enabled and not A.should_handle_ports(*B.target_port_bounds):log.debug('Received ArtPoll, but ignoring it since none of its universes overlap with our universes.');return
		if B.notify_on_change:A.node_change_subscribers.add(C[0])
		A.send_reply(C[0])
		if B.is_diagnostics_enabled:A.send_diagnostics(addr=C[0],diagnostics_mode=DiagnosticsMode.UNICAST,diagnostics_priority=B.diagnostics_priority)
	def handle_command(D,command):
		E=command
		if E.esta==65535:
			F=E.command.split('&')
			for A in F:
				A=A.strip(' ')
				if A:
					B,C=A.split('=');B=B.lower()
					if B=='SwoutText'.lower():D.swout_text=C;log.debug(f"Set Sw out text to: {C}")
					elif B=='SwinText'.lower():D.swin_text=C;log.debug(f"Set Sw in text to: {C}")
	def handle_trigger(A,trigger):0
	def handle_dmx(A,dmx):
		C=dmx;B=A.own_port_addresses.get(C.port_address)
		if not B:log.debug(f"Received ArtDmx for port address that we don't care about: {C.port_address}");return
		if B.port.good_input.data_received:B.port.good_input.data_received=_B;A.update_subscribers()
		B.port.last_input_seen=datetime.datetime.now();A.__hass.async_create_task(A.disable_input_flag(B))
		if A.__state_update_callback:A.__state_update_callback(C.port_address,C.data)
	async def disable_input_flag(B,own_port):
		A=own_port;await asyncio.sleep(4);C=datetime.datetime.now()-datetime.timedelta(seconds=4)
		if A.port.last_input_seen<C:A.port.good_input.data_received=_C;B.update_subscribers()