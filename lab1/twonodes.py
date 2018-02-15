import sys

sys.path.append('..')

from src.sim import Sim
from src.packet import Packet

from networks.network import Network


class DelayHandler(object):
	@staticmethod
	def receive_packet(packet):
		print(("Time received: " + str(Sim.scheduler.current_time()), "Packet ID: " + str(packet.ident), "Time created: " + str(packet.created)))

def main():
	d = DelayHandler()
	for i in range(1, 4):
		print("SIMULATION NO. " + str(i))
		Sim.scheduler.reset()

		net = Network('./twonodes' + str(i) + '.txt')

		n1 = net.get_node('n1')
		n2 = net.get_node('n2')
		n1.add_forwarding_entry(address=n2.get_address('n1'), link=n1.links[0])
		n2.add_forwarding_entry(address=n1.get_address('n2'), link=n2.links[0])

		net.nodes['n2'].add_protocol(protocol="delay", handler=d)

		if (i == 3):
			for j in range(0,4):
				packet = Packet(destination_address=n2.get_address('n1'), ident=j, protocol='delay', length=1000)
				if j == 3:
					delay = 2
				else:
					delay = 0
				Sim.scheduler.add(delay=delay, event=packet, handler=n1.send_packet)
		else:
			packet = Packet(destination_address=n2.get_address('n1'), ident=0, protocol='delay', length=1000)
			Sim.scheduler.add(delay=0, event=packet, handler=n1.send_packet)

		Sim.scheduler.run()

if __name__ == '__main__':
	main()
