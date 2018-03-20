
from __future__ import print_function

import sys

sys.path.append('..')

from src.sim import Sim
from src.transport import Transport
from tcp import TCP
from tcpplot import Plotter

from networks.network import Network

import optparse
import os
import subprocess


class AppHandler(object):
	def __init__(self, filename):
		self.filename = filename
		self.directory = 'received'
		if not os.path.exists(self.directory):
			os.makedirs(self.directory)
		self.f = open(os.path.join(self.directory, self.filename), 'wb')

	def receive_data(self, data):
		Sim.trace('AppHandler', "application got %d bytes" % (len(data)))
		self.f.write(data)
		self.f.flush()

class Main(object):
	def __init__(self):
		self.directory = 'received'
		self.filename = "internet-architecture.pdf"
		self.run()

	def diff(self):
		args = ['diff', '-u', self.filename, os.path.join(self.directory, self.filename)]
		result = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
		print()
		if not result:
			print("File transfer correct!")
		else:
			print("File transfer failed. Here is the diff:")
			print(result)
			quit()

	def run(self):
		drop_packets = [14000, 26000, 28000]
		Sim.set_debug('Plot')

		# setup network
		net = Network('basic.txt')

		# setup routes
		n1 = net.get_node('n1')
		n2 = net.get_node('n2')
		n1.add_forwarding_entry(address=n2.get_address('n1'), link=n1.links[0])
		n2.add_forwarding_entry(address=n1.get_address('n2'), link=n2.links[0])

		# setup transport
		t1 = Transport(n1)
		t2 = Transport(n2)

		plotter = Plotter()

		for i in range(0, 4):
			application = AppHandler(self.filename)
			Sim.scheduler.reset()
			Sim.files = {}

			# setup connection
			c1 = TCP(t1, n1.get_address('n2'), 1, n2.get_address('n1'), 1, application, fast_retransmit=True, drop=drop_packets[:i])
			TCP(t2, n2.get_address('n1'), 1, n1.get_address('n2'), 1, application, fast_retransmit=True)

			# send a file
			with open(self.filename, 'rb') as f:
				while True:
					data = f.read()
					if not data:
						break
					Sim.scheduler.add(delay=0, event=data, handler=c1.send)

			Sim.scheduler.run()
			for filename, file in Sim.files.iteritems():
				file.close()
			
			plotter.sequence("sequence" + str(i + 1) + ".png")
			plotter.cwnd("cwnd" + str(i + 1) + ".png")

			self.diff()


if __name__ == '__main__':
	m = Main()
