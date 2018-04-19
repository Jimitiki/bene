from __future__ import print_function

import sys

sys.path.append("..")

from src.sim import Sim
from src.packet import Packet

DV_DELAY = 1

class RoutingApp(object):
	def __init__(self, node):
		self.node = node
		self.initialize_dv()

		#distance vectors of this node"s neighbors - neighbor address -> distance vector
		self.neighbor_dvs = {}
		self.timers = {}
		self.print_dv()

		Sim.scheduler.add(delay=0, event="", handler=self.send_dv)

		# print("Node " + self.node.hostname + " links:")
		# for link in self.node.links:
		# 	print("Address: ", link.address, "\tHost Name: ", link.endpoint.hostname)

	def initialize_dv(self):
		#distance vector - address -> distance
		self.dv = {}
		for link in self.node.links:
			self.dv[link.address] = 0

	def receive_packet(self, packet):
		self.neighbor_dvs[packet.hostname] = packet.dv
		self.calculate_routes()
		if packet.hostname in self.timers:
			Sim.scheduler.cancel(event=self.timers[packet.hostname])
		self.timers[packet.hostname] = Sim.scheduler.add(delay=DV_DELAY * 3, event=packet.hostname, handler=self.handle_link_failure)
		
	def handle_link_failure(self, event):
		self.neighbor_dvs.pop(event)
		del self.timers[event]
		self.calculate_routes()

	def calculate_routes(self):
		self.initialize_dv()
		for neighbor, dv in self.neighbor_dvs.iteritems():
			for address, distance in dv.iteritems():
				if address not in self.dv or distance + 1 < self.dv[address]:
					self.dv[address] = distance + 1
					self.node.delete_forwarding_entry(address)
					self.node.add_forwarding_entry(address, self.node.get_link(neighbor))
		self.print_dv()

	def send_dv(self, event):
		p = Packet(destination_address=0, ttl=1, protocol="dvrouting")
		p.dv = self.dv
		p.hostname = self.node.hostname
		self.node.send_packet(p)
		Sim.scheduler.add(delay=DV_DELAY, event="", handler=self.send_dv)

	def print_dv(self):
		print(self.node.hostname + " Distance Vector:")
		for address, distance in self.dv.iteritems():
			print("\taddress: " + str(address) + "\tdistance: " + str(distance))

