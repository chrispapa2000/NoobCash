import os
import time
from argparse import ArgumentParser
import threading


def send_transactions(my_id, event:threading.Event, n_lines=100, basedir='5nodes', vm=False):
    filename = f"transactions{my_id}.txt"
    f = open(f"{basedir}/{filename}", 'r')
    ind = 0
    for line in f.readlines()[:n_lines]:
        id, amount = line.split(' ')
        id = id.replace('id', '')
        amount=amount.replace('\n', '')
        print(f"ID: {my_id} -> transaction {ind} (from:{my_id}, to:{id}, amount:{amount})")
        ind+=1

        ip = '10.0.0.'+str((my_id+1) % 6) if vm else '127.0.0.1'


        os.system(f"python3 client.py -n {my_id} -a t -r {id} -v {amount} -i {ip}")
    event.set()
    

def main(count, vm=False):
    n_lines = 100    
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
        t0 = threading.Thread(target=send_transactions, args=(0, e0, n_lines,'5nodes', vm))
        t1 = threading.Thread(target=send_transactions, args=(1, e1, n_lines,'5nodes', vm))
        t2 = threading.Thread(target=send_transactions, args=(2, e2, n_lines,'5nodes', vm))
        t3 = threading.Thread(target=send_transactions, args=(3, e3, n_lines,'5nodes', vm))
        t4 = threading.Thread(target=send_transactions, args=(4, e4, n_lines,'5nodes', vm))

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
        # init an event for each thread 
        events = [threading.Event() for _ in range(10)]
        for i in range(10):
            events[i].clear()
        threads = [threading.Thread(target=send_transactions, args=(i, events[i], n_lines,'10nodes', vm)) for i in range(10)]

        # start a timer 
        start_time = time.time()
        
        # start all thread 
        for i in range(10):
            threads[i].start()
        
        # wait for all threads to finish
        for e in events:
            e.wait()

        # stop the timer 
        end_time = time.time()
        print(f"time elapsed: {end_time-start_time} seconds")

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--count', help="5 or 10 nodes mode")
    parser.add_argument('-vm', '--vm', help="whether we are in vm environment")
    args = parser.parse_args()
    if not args.vm:
        main(int(args.count))
    else:
        main(int(args.count), vm=True)
