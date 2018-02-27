echo WITHOUT FAST RETRANSMIT
python fast-retransmit.py -w 10000 -l 0.2 > fast.log
tail -n 10 fast.log
echo WITH FAST RETRANSMIT
python fast-retransmit.py -w 10000 -l 0.2 -r > fast.log
tail -n 10 fast.log
