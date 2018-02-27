rm experiment.csv
echo "Window Size,Queueing Delay,Throughput" >> experiment.csv
python experiment.py -w 1000
python experiment.py -w 2000
python experiment.py -w 5000
python experiment.py -w 10000
python experiment.py -w 20000
