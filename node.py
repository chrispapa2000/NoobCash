import block
import wallet
from transaction import Transaction
from Crypto.Signature import PKCS1_v1_5
import requests
import transaction
from blockchain import Blockchain
import json
import os
from Crypto.PublicKey import RSA
# from queue import Queue
from collections import deque


class node:
    def __init__(self, number_of_nodes, port, host, id=None):
        # self.NBC=100;
        ##set

        #self.chain
        #self.current_id_count = 0
        #self.NBCs
        #self.wallet
        #self.id
        #self.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 
        self.host= host
        self.port = port
        self.number_of_nodes = number_of_nodes

        self.current_id_count = 0

        if id:
            self.id = id

        self.ring = []

        # we store UTXOs for every node 
        self.UTXOs = dict()

        self.create_wallet(port=port)

        self.blockchain = Blockchain()

        self.transaction_pool = deque() 

    #---Initialization Functions---

    # function used by non bootstrap nodes to request participation in the blockchain
    def request_participation(self):
        # if you are not the bootstrap server, you request participation from the bootstrap server
        # make a get request
        bootstrap_url = 'http://127.0.0.1:5000'
        # with app.app_context():
        # files = {'upload_file': open(f"personal_keys/public_{self.port}.pem",'rb')}
        (n,e) = self.get_my_public_key_tuple()
        response = requests.post(f"{bootstrap_url}/participate/{self.host}/{self.port}/{n}/{e}")
        response_json = response.json()
        print(response_json['id'])
        self.set_id(id=response_json['id'])

    # function that initializes the blockchain in the bootstrap node
    def initialize_blockchain(self):
        # create first transaction
        t0 = transaction.Transaction(sender_address=0, recipient_address=self.get_my_public_key_tuple(), sender_private_key=None, value=100*self.number_of_nodes,
                                    transaction_inputs=[{"transaction_id":0, "receiver_address":0, "amount":100*self.number_of_nodes}])

        # create genesis block
        genesis_block = block.Block(previousHash=1,index=0)

        # add the first transaction to the block
        genesis_block.add_transaction(t0)
        genesis_block.set_nonce(0)

        # add the genesis block to the blockchain
        self.blockchain.add_block(genesis_block)

        self.UTXOs[self.get_my_public_key_tuple()] = [{"transaction_id":0, "receiver_address":0, "amount":100*self.number_of_nodes}]

    # function that broadcast info gathered by the bootstrap node to all other nodes
    def broadcast_participants(self):
        # get all pub key files names 
        files = dict()
        files["ring"]=json.dumps({"ring":self.get_ring()}) 

        # files = {'file1': open('report.xls', 'rb'), 'file2': open('otherthing.txt', 'rb')}
        for other_node in self.get_ring():
            if other_node['id'] != self.id:
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_participants_info'
                response = requests.post(url, files=files)
    
    # function that broadcasts the initial blockhain from the bootstrap node to the other nodes 
    def broadcast_blockchain(self):
        for other_node in self.get_ring():
            if other_node['id'] != self.id:
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_initial_blockchain'
                blkchain = self.get_blockchain()
                # print(blkchain.get_chain())
                # print()
                self.get_blockchain().to_pickle(filename="blockchain.pkl")
                files = {'blockchain_file': open(f"pickles/blockchain.pkl",'rb')}
                response = requests.post(url, files=files)



    #---Normal Class Functions---
    def set_id(self, id):
        self.id = id

    def get_id_count(self):
        return self.current_id_count	
    
    def inc_id_count(self):
        self.current_id_count += 1

    def get_my_public_key_tuple(self):
        return self.wallet.get_public_key_tuple()
    
    def get_UTXOs(self, id):
        return self.UTXOs[id]
    
    def set_UTXOs(self, id, nbcList):
        self.UTXOs[id] = nbcList

    def get_ring(self):
        return self.ring
    
    def set_ring(self, ring):
        self.ring = ring

    def get_blockchain(self):
        return self.blockchain
    
    def set_blockchain(self, chain):
        self.blockchain.set_chain(chain)
    
    def create_new_block(self, previousHash):
        self.current_block = block.Block(previousHash=previousHash)

    def create_wallet(self, port):
        #create a wallet for this node, with a public key and a private key
        self.wallet = wallet.wallet()

    def get_key_from_tuple(self,n,e,d=None):
        if not d:
            key = RSA.construct((n,e))
        else:
            key = RSA.construct((n,e,d))
        return key.public_key()

    def register_node_to_ring(self, id, public_key, remote_ip, remote_port, balance=0):
        #add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
        #bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
        (n,e) = public_key
        new_node = {
            'id':id,
            'public_key':{'n':n, 'e':e},
            'remote_ip':remote_ip,
            'remote_port':remote_port,
            'balance':balance
        } 
        self.ring.append(new_node)
        pass

    # def create_transaction(sender_address, receiver_address, signature):
    def create_transaction(self, sender_address, receiver_address, private_key,value,do_broadcast=True):
        #remember to broadcast it
        
        # find UTXOs to send
        myUTXOs = self.get_UTXOs(sender_address)
        total = value
        transaction_inputs = []

        # calc transaction inputs
        for item in myUTXOs:
            total -= item["amount"]
            transaction_inputs.append(item)
            if total <= 0:
                break
        

        # initialize transaction
        trans = Transaction(sender_address=sender_address, recipient_address=receiver_address, sender_private_key=private_key, value=value, 
              transaction_inputs=transaction_inputs)
        
        # remove spent UTXOs from your UTXOS
        myUTXOs = [utxo for utxo in myUTXOs if utxo not in transaction_inputs]
        self.set_UTXOs(sender_address, myUTXOs)
        
        transaction_outputs = trans.to_dict()['transaction_outputs']
        for output in transaction_outputs:
            receiver = output['receiver_address']
            utxos = self.get_UTXOs(receiver)
            utxos.append(output)
            self.set_UTXOs(receiver, utxos)

        
        # add to block
        # self.current_block.add_transaction(trans)

        # broadcast
        if do_broadcast:
            self.broadcast_transaction(trans)

        return trans

        

    def broadcast_transaction(self, trans:Transaction):
        for other_node in self.get_ring():
            url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_transaction'
            trans.to_pickle("trans.pkl")
            files = {'transaction_file': open(f"pickles/trans.pkl",'rb')}
            response = requests.post(url, files=files)

    # test

    def verify_signature(self, trans:Transaction):
        #use of signature and NBCs balance
        # check signature
        trans_dict = trans.to_dict()
        # signer object
        singer = PKCS1_v1_5.new(trans_dict['sender_address'])
        # hash object
        hash_object = trans_dict["transaction_id"]
        #signature
        signature = trans_dict["signature"]

        # verify
        try:
            singer.verify(hash_object, signature=signature)
            # print("Succesful Verification")
            return True
        except:
            # print("Problem Verifying")
            return False


    def update_UTXOs(self, sender, transaction_inputs, transaction_outputs):
        self.UTXOs[sender] = list(set(self.UTXOs[sender]).difference(set(transaction_inputs)))
        for output in transaction_outputs:
            receiver = output['receiver_address']
            self.UTXOs[receiver] = self.UTXOs['receiver'].append(output)
        

    def validate_transaction(self, trans: Transaction):
        if not self.verify_signature():
            return False
         
        # check NBCs balance
        trans_dict = trans.to_dict()

        trans_inputs = trans_dict["transaction_inputs"]
        sender = trans_dict["sender_address"]
        for item in trans_inputs:
            if item not in self.get_UTXOs(sender):
                return False
        
        self.update_UTXOs(trans_dict["sender_address"], trans_dict["transaction_inputs"], trans_dict["transaction_outputs"])

        self.mempool.put(trans)

    def add_transaction_to_block(self):
        #if enough transactions  mine
        if self.current_block.is_filled():
            self.mine_block()


    def mine_block(self):
        #nonce = self.current_block.get_nonce()
        difficulty = self.blockchain.get_difficulty()
        proof  = '0'*difficulty
        #prev_hash  = str(self.current_block.previousHash)
        #transactions = str(self.current_block.listOfTransactions)
        #static_str = prev_hash + transactions
        while self.current_block.hash[:difficulty] != proof:
            
            self.current_block.nonce += 1
            #hash string
            #hash1 = hashlib.sha256(whole_str.encode()).hexdigest()
            self.current_block.calc_hash()
            #check with difficulty



    def broadcast_block():
        pass


        

    # def valid_proof(.., difficulty=MINING_DIFFICULTY):
    # 	pass




    # #concencus functions

    # def valid_chain(self, chain):
    # 	#check for the longer chain accroose all nodes
    # 	pass


    # def resolve_conflicts(self):
    # 	#resolve correct chain
    # 	pass



