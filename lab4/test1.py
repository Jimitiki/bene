from __future__ import print_function

import sys
from routing import RoutingApp

sys.path.append("..")

from networks.network import Network
from src.sim import Sim
from src.packet import Packet

SIM_RUN_TIME = 2.8

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
	net = Network("test1network.txt")
	for hostname, node in sorted(net.nodes.iteritems()):
		node.add_protocol(protocol="dvrouting", handler=RoutingApp(node))

	n5 = net.get_node("n5")
	n5.add_protocol(protocol="delay", handler=DelayHandler())

	p = Packet(destination_address=n5.get_address("n4"), ident=1, protocol="delay", length=1000)
	n1 = net.get_node("n1")
	Sim.scheduler.add(delay=3.2, event=p, handler=n1.send_packet)

	# run the simulation
	Sim.scheduler.run()

if __name__ == "__main__":
	main()