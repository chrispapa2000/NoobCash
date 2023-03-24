import os
import time
from argparse import ArgumentParser
import threading


def send_transactions(my_id, event:threading.Event, n_lines=100, basedir='5nodes'):
    filename = f"transactions{my_id}.txt"
    f = open(f"{basedir}/{filename}", 'r')
    ind = 0
    for line in f.readlines()[:n_lines]:
        id, amount = line.split(' ')
        id = id.replace('id', '')
        amount=amount.replace('\n', '')
        print(f"ID: {my_id} -> transaction {ind} (from:{my_id}, to:{id}, amount:{amount})")
        ind+=1

        # ip = '10.0.0.'+str(my_id+1)
        ip = '127.0.0.1'


        os.system(f"python3 client.py -n {my_id} -a t -r {id} -v {amount} -i {ip}")
    event.set()
    

def main(count):
    if count == 5:
        e0 = threading.Event()
        e0.clear()
        e1 = threading.Event()
        e1.clear()
        e2 = threading.Event()
        e2.clear()
        e3 = threading.Event()
        e3.clear()
        e4 = threading.Event()
        e4.clear()
        t0 = threading.Thread(target=send_transactions, args=(0, e0, 100,'5nodes'))
        t1 = threading.Thread(target=send_transactions, args=(1, e1, 100,'5nodes'))
        t2 = threading.Thread(target=send_transactions, args=(2, e2,100,'5nodes'))
        t3 = threading.Thread(target=send_transactions, args=(3, e3, 100,'5nodes'))
        t4 = threading.Thread(target=send_transactions, args=(4, e4, 100,'5nodes'))

        start_time = time.time()
        
        t0.start()
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        e0.wait()
        e1.wait()
        e2.wait()
        e3.wait()
        e4.wait()
        end_time = time.time()
        print(f"time elapsed: {end_time-start_time} seconds")

    elif count == 10:
        pass

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--count', help="5 or 10 nodes mode")
    args = parser.parse_args()
    main(int(args.count))
