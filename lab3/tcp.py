from __future__ import print_function
from src.buffer import SendBuffer, ReceiveBuffer
from src.connection import Connection
from src.sim import Sim
from src.tcppacket import TCPPacket

class TCP(Connection):
	""" A TCP connection between two hosts."""

	def __init__(self, transport, source_address, source_port,
				 destination_address, destination_port, app=None,drop=[],
				 fast_retransmit=False, measure=False):
		Connection.__init__(self, transport, source_address, source_port,
							destination_address, destination_port, app)

		# -- Sender functionality

		# send buffer
		self.send_buffer = SendBuffer()
		# maximum segment size, in bytes
		self.mss = 1000
		# initial cwnd is equal to 1mss
		self.cwnd = float(self.mss)
		# boolean flag that indicates if in slow start or additive increase
		self.slow_start = True
		# When cwnd >= ss_thresh, slow start ends
		self.ss_thresh = 100000
		if self.node.hostname == 'n1':
			self.trace("Entering Slow Start: SS Thresh = %s" % (self.ss_thresh))
		# Tracks additive increase - determines when to add another MSS to cwnd
		self.cwnd_inc = 0

		# largest sequence number that has been ACKed so far; represents
		# the next sequence number the client expects to receive
		self.sequence = 0
		# plot sequence numbers
		self.plot_sequence_header()
		self.plot_cwnd_header()
		self.plot_cwnd()
		# packets to drop
		self.drop = drop
		self.dropped = []
		# retransmission timer
		self.timer = None
		# timeout duration in seconds
		self.timeout = 1


		# -- Receiver functionality

		# receive buffer
		self.receive_buffer = ReceiveBuffer()
		# ack number to send; represents the largest in-order sequence
		# number not yet received
		self.ack = 0
		self.fast_retransmit = fast_retransmit
		self.last_ack = 0
		self.last_ack_count = 0

	def trace(self, message):
		""" Print debugging messages. """
		Sim.trace("TCP", message)

	def plot_sequence_header(self):
		if self.node.hostname =='n1':
			Sim.plot('sequence.csv','Time,Sequence Number,Event\n')

	def plot_sequence(self,sequence,event):
		if self.node.hostname =='n1':
			Sim.plot('sequence.csv','%s,%s,%s\n' % (Sim.scheduler.current_time(), sequence,event))

	def plot_cwnd_header(self):
		if self.node.hostname =='n1':
			Sim.plot('cwnd.csv','Time,Congestion Window\n')

	def plot_cwnd(self):
		if self.node.hostname =='n1':
			Sim.plot('cwnd.csv','%s,%s\n' % (Sim.scheduler.current_time(),int(self.cwnd)))

	def receive_packet(self, packet):
		""" Receive a packet from the network layer. """
		if packet.ack_number > 0:
			# handle ACK
			self.handle_ack(packet)
		if packet.length > 0:
			# handle data
			self.handle_data(packet)

	''' Sender '''

	def send(self, data):
		""" Send data on the connection. Called by the application."""
		
		self.send_buffer.put(data)
		self.send_window()

	def send_window(self):
		while self.send_buffer.outstanding() < self.cwnd and self.send_buffer.available() > 0:
			(packet_data, self.sequence) = self.send_buffer.get(self.mss)
			self.send_packet(packet_data, self.sequence)

	def send_packet(self, data, sequence):
		packet = TCPPacket(source_address=self.source_address,
						   source_port=self.source_port,
						   destination_address=self.destination_address,
						   destination_port=self.destination_port,
						   body=data,
						   sequence=sequence, ack_number=self.ack)

		if sequence in self.drop and not sequence in self.dropped:
			self.dropped.append(sequence)
			self.plot_sequence(sequence,'drop')
			self.trace("%s (%d) dropping TCP segment to %d for %d" % (
				self.node.hostname, self.source_address, self.destination_address, packet.sequence))
			self.trace("PACKET DROPPED CWND IS %s\n" % (self.cwnd))
			return

		# send the packet
		self.plot_sequence(sequence,'send')
		self.trace("%s (%d) sending TCP segment to %d for %d" % (
			self.node.hostname, self.source_address, self.destination_address, packet.sequence))
		self.transport.send_packet(packet)

		# set a timer
		if not self.timer:
			self.start_retransmit_timer(self.timeout)

	def handle_ack(self, packet):
		""" Handle an incoming ACK. """
		self.plot_sequence(packet.ack_number - 1000,'ack')
		prev_out = self.send_buffer.outstanding()
		self.send_buffer.slide(packet.ack_number)
		bytes_acked = prev_out - self.send_buffer.outstanding()
		self.trace("%s (%d) received ACK from %d for %d. %d bytes ACKed" % (
			self.node.hostname, packet.destination_address, packet.source_address, packet.ack_number, bytes_acked))

		if self.fast_retransmit:
			if self.last_ack == packet.ack_number:
				self.last_ack_count += 1
				if self.last_ack_count == 4:
					self.retransmit(None)
			elif packet.ack_number > self.last_ack:
				self.last_ack = packet.ack_number
				self.last_ack_count = 1

		if bytes_acked > 0:
			if self.slow_start:
				self.cwnd += self.mss
				self.plot_cwnd()
				if self.cwnd == self.ss_thresh:
					self.slow_start = False
					self.trace("Entering Additive Increase: CWND = %s" % (self.cwnd))
			else:
				self.cwnd_inc += self.mss * bytes_acked / self.cwnd
				if self.cwnd_inc > self.mss:
					self.cwnd += self.mss
					self.cwnd_inc -= self.mss
					self.plot_cwnd()



		# self.trace("Window Size: %f" % (self.cwnd))
		self.cancel_timer()
		if not self.send_buffer.outstanding() == 0:
			self.start_retransmit_timer(self.timeout)
		self.send_window()	

	def retransmit(self, event):
		""" Retransmit data. """
		self.ss_thresh = max(self.cwnd/2, self.mss)
		self.ss_thresh -= self.ss_thresh % self.mss
		self.slow_start = True
		self.cwnd = float(self.mss)
		self.trace("Entering Slow Start: SS Thresh = %s CWND = %s" % (self.ss_thresh, self.cwnd))
		self.plot_cwnd()
		self.cwnd_inc = 0.0
		if event:
			self.trace("%s (%d) retransmission timer fired" % (self.node.hostname, self.source_address))
			self.timer = None
		else:
			self.trace("%s (%d) Fast retransmit occured" % (self.node.hostname, self.source_address))
			
		(data, sequence) = self.send_buffer.resend(size=self.mss, reset=True)
		if len(data) == 0:
			return
		self.send_packet(data, sequence)

	def start_retransmit_timer(self, time):
		self.timer = Sim.scheduler.add(delay=time, event='retransmit', handler=self.retransmit)

	def cancel_timer(self):
		""" Cancel the timer. """
		if not self.timer:
			return
		Sim.scheduler.cancel(self.timer)
		self.timer = None

	''' Receiver '''

	def handle_data(self, packet):
		""" Handle incoming data. This code currently gives all data to
			the application, regardless of whether it is in order, and sends
			an ACK."""
		# self.trace("%s (%d) received TCP segment from %d for %d" % (
			# self.node.hostname, packet.destination_address, packet.source_address, packet.sequence))

		self.receive_buffer.put(packet.body, packet.sequence)
		(buffer_data, sequence_number) = self.receive_buffer.get()
		if len(buffer_data) > 0:
			self.app.receive_data(buffer_data)
		
		if sequence_number == packet.sequence:
			self.ack = packet.sequence + len(buffer_data)

		self.send_ack()

	def send_ack(self):
		""" Send an ack. """
		packet = TCPPacket(source_address=self.source_address,
						   source_port=self.source_port,
						   destination_address=self.destination_address,
						   destination_port=self.destination_port,
						   sequence=self.sequence, ack_number=self.ack)
		# send the packet
		self.trace("%s (%d) sending TCP ACK to %d for %d" % (
			self.node.hostname, self.source_address, self.destination_address, packet.ack_number))
		self.transport.send_packet(packet)
