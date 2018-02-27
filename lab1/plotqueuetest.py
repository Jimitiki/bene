import numpy
import pandas as pd
import matplotlib.pyplot as plt

def main():
	network_loads = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.78, 0.8, 0.9, 0.95, 0.98]

	delay_avgs = []
	tags = []
	for i in range(0, 12):
		load = network_loads[i]
		delay_sum = 0
		sample_count = 0
		f = open("./queueingtest" + str(i + 1) + ".csv")
		for line in f:
			delay_sum += float(line)
			sample_count += 1

		f.close()
		delay_avgs.append(delay_sum / sample_count)
		tags.append(str(network_loads[i]))

	theory_loads = numpy.linspace(.0001, .98, 200)
	mu = 1000000 / 8000.0
	theory_delay = 1 / (mu * theory_loads) * theory_loads / (1 - theory_loads)

	# print("YEE")
	actual_data = {"Utilization": network_loads,
			"Actual Delay": delay_avgs}

	theory_data = {"Utilization": theory_loads,
			"Theoretical Delay": theory_delay}

	actual_df = pd.DataFrame(actual_data)
	theory_df = pd.DataFrame(theory_data)
	ax = actual_df.plot(x="Utilization", y="Actual Delay")
	ax.set_xlabel("Utilization")
	ax.set_ylabel("Queueing Delay")
	theory_df.plot(x="Utilization", y="Theoretical Delay", ax=ax)

	fig = ax.get_figure()
	# print("AAAYYYYY")
	fig.savefig('./line.png')

if __name__ == "__main__":
	main()
		