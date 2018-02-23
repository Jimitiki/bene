echo TEST 1
python basic.py -w 3000 > basic.log
tail -n 7 basic.log
echo TEST 2
python basic.py -w 3000 -l 0.1 > basic.log
tail -n 7 basic.log
echo TEST 3
python basic.py -w 3000 -l 0.2 > basic.log
tail -n 7 basic.log
echo TEST 4
python basic.py -w 3000 -l 0.5 > basic.log
tail -n 7 basic.log
echo TEST 5
python basic.py -w 10000 -f internet-architecture.pdf > basic.log
tail -n 7 basic.log
echo TEST 6
python basic.py -w 10000 -l 0.5 -f internet-architecture.pdf > basic.log
tail -n 7 basic.log
