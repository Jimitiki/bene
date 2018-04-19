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
	net = Network("test3network.txt")
	for hostname, node in sorted(net.nodes.iteritems()):
		node.add_protocol(protocol="dvrouting", handler=RoutingApp(node))

	n7 = net.get_node("n7")
	n7.add_protocol(protocol="delay", handler=DelayHandler())
	n10 = net.get_node("n10")
	n10.add_protocol(protocol="delay", handler=DelayHandler())
	n15 = net.get_node("n15")
	n15.add_protocol(protocol="delay", handler=DelayHandler())

	n8 = net.get_node("n8")
	n11 = net.get_node("n11")
	n12 = net.get_node("n12")

	p1 = Packet(destination_address=n7.get_address("n6"), ident=1, protocol="delay", length=1000)
	Sim.scheduler.add(delay=4.2, event=p1, handler=n12.send_packet)
	p3 = Packet(destination_address=n15.get_address("n14"), ident=2, protocol="delay", length=1000)
	Sim.scheduler.add(delay=4.3, event=p3, handler=n11.send_packet)
	p2 = Packet(destination_address=n10.get_address("n1"), ident=3, protocol="delay", length=1000)
	Sim.scheduler.add(delay=4.4, event=p2, handler=n8.send_packet)

	n2 = net.get_node("n2")
	Sim.scheduler.add(delay=4.8, event=None, handler=n2.get_link("n8").down)
	Sim.scheduler.add(delay=4.8, event=None, handler=n8.get_link("n2").down)

	p4 = Packet(destination_address=n10.get_address("n1"), ident=4, protocol="delay", length=1000)
	Sim.scheduler.add(delay=10.4, event=p4, handler=n8.send_packet)

	Sim.scheduler.add(delay=10.8, event=None, handler=n2.get_link("n8").up)
	Sim.scheduler.add(delay=10.8, event=None, handler=n8.get_link("n2").up)

	p5 = Packet(destination_address=n10.get_address("n1"), ident=5, protocol="delay", length=1000)
	Sim.scheduler.add(delay=16.4, event=p5, handler=n8.send_packet)

	# run the simulation
	Sim.scheduler.run()

if __name__ == "__main__":
	main()