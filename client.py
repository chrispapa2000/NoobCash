from argparse import ArgumentParser
import requests
import json

def make_transaction_request(recipient_id, amount, port, ip):
    host = 'http://'+ip+':'+str(port)
    url = f"{host}/get_transaction_from_cli/{recipient_id}/{amount}"
    response = requests.post(url,)
    if response.json() == "OK":
        print("transaction successful")
    else:
        print("There is not enough money for this transaction")
    # print(response.json())

def make_view_request(port, ip):
    host = 'http://'+ip+':'+str(port)
    url = f"{host}/view_transactions"
    response = requests.get(url,)
    response = response.json()['last_transactions']
    print("transactions in the last block:")
    ind = 0
    for item in response:
        print(f"{ind} : {item}")
        ind+=1

def make_balance_request(port, ip):
    host = 'http://'+ip+':'+str(port)
    url = f"{host}/balance"
    response = requests.get(url,)
    balance = response.json()['balance']
    print(f"Your current balance: {balance}")


def main():
    parser = ArgumentParser()
    parser.add_argument('-i', '--ip', help="The ip of the host that we want to access")
    parser.add_argument('-n', '--node', required=True, help="The id of the node that we want to access")
    parser.add_argument('-a', '--action', required='True', choices=['t','view','balance'], help="The action to execute: 't' indicates that we want to do a transaction,\
                        'view' shows the transactions included in the last validated block and 'balance' shows your account's balance.")
    parser.add_argument('-r', '--recipient', required=False, help="The id of the Transaction's recipient. Only used it the action is 't'.")
    parser.add_argument('-v', '--value', required=False, help="The amount of NoobCash that the Transaction transfers to the recipient. Omly used if the action is 't'.")
    args = parser.parse_args()
    
    ports = [i for i in range(5000, 6000, 100)]
    port = ports[int(args.node)]
    if not args.ip:
        args.ip = '127.0.0.1'

    if not args.action in ['t','view','balance']:
        parser.print_help()
        return
    else:
        if args.action == 't':
            if (not args.recipient) or (not args.value):
                parser.print_help()
                return
            else:
                id = int(args.recipient.replace("id",""))
                make_transaction_request(recipient_id=id, amount=int(args.value), port=port,ip=args.ip)
        elif args.action == 'view':
            # print("Action: view")
            make_view_request(port=port, ip=args.ip)

        elif args.action == 'balance':
            # print("Action: balance")
            make_balance_request(port=port, ip=args.ip)

if __name__=='__main__':
    main()
