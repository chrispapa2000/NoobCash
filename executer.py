import os
import time
from argparse import ArgumentParser

def send_transactions(my_id, n_lines=100, basedir='5nodes'):
    filename = f"transactions{my_id}.txt"
    f = open(f"{basedir}/{filename}", 'r')
    ind = 0
    for line in f.readlines()[:n_lines]:
        id, amount = line.split(' ')
        id = id.replace('id', '')
        amount=amount.replace('\n', '')
        print(f"transaction {ind} (from:{my_id}, to:{id}, amount:{amount})")
        ind+=1
        # print(id)
        # print(amount)
        os.system(f"python3 client.py -n {my_id} -a t -r {id} -v {amount}")
        time.sleep(0.1)

def main(my_id):
    send_transactions(my_id, n_lines=20, basedir='10nodes')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-n', '--node', help="the id of the node that executed the transactions")
    args = parser.parse_args()
    main(int(args.node))
