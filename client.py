from argparse import ArgumentParser
import requests

def make_request(recipient_id, amount, port):
    host = 'http://127.0.0.1:'+str(port)
    url = f"{host}/get_transaction_from_cli/{recipient_id}/{amount}"
    response = requests.post(url,)

def main():
    parser = ArgumentParser()
    parser.add_argument('-n', '--node', required=True, help="The id of the node that we want to access")
    parser.add_argument('-a', '--action', choices=['t','view','balance'], help="The action to execute: 't' indicates that we want to do a transaction,\
                        'view' shows the transactions included in the last validated block and 'balance' shows your account's balance.")
    parser.add_argument('-r', '--recipient', required=False, help="The id of the Transaction's recipient. Only used it the action is 't'.")
    parser.add_argument('-v', '--value', required=False, help="The amount of NoobCash that the Transaction transfers to the recipient. Omly used if the action is 't'.")
    args = parser.parse_args()
    
    ports = [5000, 6000, 7000, 8000, 9000]
    port = ports[int(args.node)]

    if not args.action in ['t','view','balance']:
        print("help message")
        return
    else:
        if args.action == 't':
            if (not args.recipient) or (not args.value):
                print("help message")
                return
            else:
                id = int(args.recipient.replace("id",""))
                make_request(recipient_id=id, amount=int(args.value), port=port)
        elif args.action == 'view':
            print("Action: view")
        elif args.action == 'balance':
            print("Action: balance")

if __name__=='__main__':
    main()