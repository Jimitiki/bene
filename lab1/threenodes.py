import sys

sys.path.append('..')

from src.sim import Sim
from src.packet import Packet

from networks.network import Network

class DelayHandler(object):
	@staticmethod
	def receive_packet(packet):
		print(("Time received: " + str(Sim.scheduler.current_time()),
		 		"Packet ID: " + str(packet.ident), 
		 		"Time created: " + str(packet.created)))

def main():
	d = DelayHandler()
	for i in range(1, 4):
		Sim.scheduler.reset()

		net = Network('./threenodes' + str(i) + '.txt')

		n1 = net.get_node('n1')
		n2 = net.get_node('n2')
		n3 = net.get_node('n3')
		n1.add_forwarding_entry(address=n2.get_address('n1'), link=n1.links[0])
		n1.add_forwarding_entry(address=n3.get_address('n2'), link=n1.links[0])
		n2.add_forwarding_entry(address=n3.get_address('n2'), link=n2.links[1])

		net.nodes['n3'].add_protocol(protocol="delay", handler=d)

		n1_transmission_delay = 8000.0 / n1.links[0].bandwidth

		for j in range(0, 1001):
			protocol = None
			if (j > 995):
				protocol = 'delay'

			packet = Packet(destination_address=n3.get_address('n2'), ident=j, protocol=protocol, length=1000)
			delay = j * n1_transmission_delay
			Sim.scheduler.add(delay=delay, event=packet, handler=n1.send_packet)

		Sim.scheduler.run()
		print("\n")

if __name__ == '__main__':
	main()
