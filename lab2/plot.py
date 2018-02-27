import numpy
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams.update({'figure.autolayout': True})

data = pd.read_csv("./experiment.csv")

plt.figure()
ax = data.plot(x='Window Size',y='Queueing Delay')
ax.set_xlabel("Window Size (bytes)")
ax.set_ylabel("Average Queueing Delay (seconds)")
fig = ax.get_figure()
fig.savefig('delay.png')

plt.figure()
ax = data.plot(x='Window Size',y='Throughput')
ax.set_xlabel("Window Size (bytes)")
ax.set_ylabel("Throughput (seconds)")
fig = ax.get_figure()
fig.savefig('throughput.png')
		