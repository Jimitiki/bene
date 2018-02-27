
from __future__ import print_function

import sys

sys.path.append('..')

from src.sim import Sim
from src.transport import Transport
from tcp import TCP

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
		self.parse_options()
		self.run()
		self.filename = None

	def parse_options(self):
		parser = optparse.OptionParser(usage="%prog [options]",
									   version="%prog 0.1")

		parser.add_option("-w", "--window", type="int", dest="window",
							default=1000,
							help="TCP connection window size")

		(options, args) = parser.parse_args()
		self.fast_retransmit = True
		self.filename = "internet-architecture.pdf"
		self.loss = 0.0
		self.window = options.window

	def run(self):
		# parameters
		Sim.scheduler.reset()

		# setup network
		net = Network('experiment.txt')
		net.loss(self.loss)

		# setup routes
		n1 = net.get_node('n1')
		n2 = net.get_node('n2')
		n1.add_forwarding_entry(address=n2.get_address('n1'), link=n1.links[0])
		n2.add_forwarding_entry(address=n1.get_address('n2'), link=n2.links[0])

		# setup transport
		t1 = Transport(n1)
		t2 = Transport(n2)

		# setup application
		a = AppHandler(self.filename)

		# setup connection
		c1 = TCP(t1, n1.get_address('n2'), 1, n2.get_address('n1'), 1, a, window=self.window, fast_retransmit=self.fast_retransmit, measure=True)
		TCP(t2, n2.get_address('n1'), 1, n1.get_address('n2'), 1, a, window=self.window, fast_retransmit=self.fast_retransmit, measure=True)

		# send a file
		with open(self.filename, 'rb') as f:
			while True:
				data = f.read()
				if not data:
					break
				Sim.scheduler.add(delay=0, event=data, handler=c1.send)

		Sim.scheduler.run()
		result_file = open("results.txt", "r")
		results = result_file.read()
		result_file.close()
		f = open("experiment.csv", "a")
		f.write(str(self.window) + "," + results + "\n")

if __name__ == '__main__':
	m = Main()
