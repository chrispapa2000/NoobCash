import os
import time
from argparse import ArgumentParser

def send_transactions(my_id, n_lines=100, basedir='5nodes'):
    filename = f"transactions{my_id}.txt"
    f = open(f"{basedir}/{filename}", 'r')
    ind = 0
    start=time.time()
    for line in f.readlines()[:n_lines]:
        id, amount = line.split(' ')
        id = id.replace('id', '')
        amount=amount.replace('\n', '')
        print(f"transaction {ind} (from:{my_id}, to:{id}, amount:{amount})")
        ind+=1
        # print(id)
        # print(amount)
        ip = '10.0.0.'+str(my_id+1)
        os.system(f"python3 client.py -n {my_id} -a t -r {id} -v {amount} -i {ip}")
        # time.sleep(0.1)
    end = time.time()  
    time_elapsed = end-start
    print(f"time elapsed: {time_elapsed}, start: {start}, end: {end}")

def main(my_id):
    send_transactions(my_id, n_lines=100, basedir='5nodes')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-n', '--node', help="the id of the node that executed the transactions")
    args = parser.parse_args()
    main(int(args.node))
