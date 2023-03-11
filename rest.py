import requests
import node
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

port = 0
host = ""

# import block
# import node
# import blockchain
# import wallet
# import transaction

### JUST A BASIC EXAMPLE OF A REST API WITH FLASK



app = Flask(__name__)
CORS(app)
# blockchain = Blockchain()


#.......................................................................................

# function used by non bootstrap nodes to request participation in the blockchain
def request_participation():
    # if you are not the bootstrap server, you request participation from the bootstrap server
    # make a get request
    bootstrap_url = 'http://127.0.0.1:5000'
    public_key = 1
    with app.app_context():
        response = requests.get(f"{bootstrap_url}/participate/{public_key}/{host}/{port}")
        response_json = response.json()
        print(response_json['id'])
        node.id = response_json['id']


# route called in the bootstrap node to allow other nodes to participate
@app.route('/participate/<public_key>/<remote_ip>/<remote_port>', methods=['GET'])
def participate(public_key, remote_ip, remote_port):
    node.current_id_count += 1
    id = node.current_id_count
    node.register_node_to_ring(id, public_key, remote_ip, remote_port, balance=0)
    resp = {"id":node.current_id_count}

    print("--------------------")
    print("received subscription request")
    print("current ring:", node.ring)
    print("--------------------")
    return jsonify(resp), 200


# get all transactions in the blockchain

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200



# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-b', '--bootstrap', default=0, type=int, help='a value of 1 indicates that this is the boostrap node')
    args = parser.parse_args()
    port = args.port
    host = '127.0.0.1'

    # only for bootstrap node
    if args.bootstrap == 1:
        node = node.node(id=id)
    else:
        node = node.node()   
        request_participation()
    app.run(host=host, port=port)

