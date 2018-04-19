from __future__ import print_function

import sys
from routing import RoutingApp

sys.path.append("..")

from networks.network import Network
from src.sim import Sim
from src.packet import Packet

class DelayHandler(object):
    @staticmethod
    def receive_packet(packet):
        print((Sim.scheduler.current_time(),
               packet.ident,
               packet.created,
               Sim.scheduler.current_time() - packet.created,
               packet.transmission_delay,
               packet.propagation_delay,
               packet.queueing_delay))

def main():
	# parameters
	Sim.scheduler.reset()
	Sim.set_debug("Node")

	# setup network
	net = Network("test2network.txt")
	for hostname, node in sorted(net.nodes.iteritems()):
		node.add_protocol(protocol="dvrouting", handler=RoutingApp(node))

	n3 = net.get_node("n3")
	n3.add_protocol(protocol="delay", handler=DelayHandler())

	p = Packet(destination_address=n3.get_address("n2"), ident=1, protocol="delay", length=1000)
	n2 = net.get_node("n2")
	Sim.scheduler.add(delay=1.2, event=p, handler=n2.send_packet)
	Sim.scheduler.add(delay=1.6, event=None, handler=n2.get_link("n3").down)
	Sim.scheduler.add(delay=1.6, event=None, handler=n3.get_link("n2").down)

	p = Packet(destination_address=n3.get_address("n2"), ident=2, protocol="delay", length=1000)
	Sim.scheduler.add(delay=6.6, event=p, handler=n2.send_packet)

	# run the simulation
	Sim.scheduler.run()

if __name__ == "__main__":
	main()