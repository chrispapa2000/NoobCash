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
from collections import deque
from threading import Lock
import pickle
from Crypto.Hash import SHA
import binascii
from threading import Thread
import time
import random
from termcolor import colored


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

        self.id = id

        # self.ring = []
        self.ring_dict = dict()

        # we store UTXOs for every node 
        self.UTXOs = dict()

        self.create_wallet(port=port)

        self.blockchain = Blockchain()

        self.transaction_pool = deque() 

        self.mining_now = False

        self.current_block = block.Block(index=None, previousHash=None)

        # locks
        self.transaction_pool_lock = Lock()
        self.blockchain_lock = Lock()
        self.current_block_lock = Lock()
        self.balances_lock = Lock() 
        self.UTXO_lock = Lock()

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
                                     transaction_inputs=[{"transaction_id":0, "receiver_address":self.get_my_public_key_tuple(), "amount":100*self.number_of_nodes}])

        # create genesis block
        genesis_block = block.Block(previousHash=1,index=0)

        # add the first transaction to the block
        genesis_block.add_transaction(t0)
        genesis_block.set_nonce(0)

        # add the genesis block to the blockchain
        self.blockchain.add_block(genesis_block)

        self.current_block = block.Block(index=1, previousHash=genesis_block.hash)

        self.UTXOs[self.get_my_public_key_tuple()] = [{"transaction_id":0, "receiver_address":self.get_my_public_key_tuple(), "amount":100*self.number_of_nodes}]

    # function that broadcast info gathered by the bootstrap node to all other nodes
    def broadcast_participants(self):
        # get all pub key files names 
        files = dict()
        files["ring"]=pickle.dumps(self.ring_dict) 

        # files = {'file1': open('report.xls', 'rb'), 'file2': open('otherthing.txt', 'rb')}
        for other_node in self.ring_dict.values():
            if other_node['id'] != self.id:
                print(other_node)
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_participants_info'
                response = requests.post(url, files=files)
        # self.ring_to_dict()

    # function that broadcasts the initial blockhain from the bootstrap node to the other nodes 
    def broadcast_blockchain(self):
        for other_node in self.ring_dict.values():
            if other_node['id'] != self.id:
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_initial_blockchain'
                blkchain = self.get_blockchain()
                # print(blkchain.get_chain())
                # print()
                # self.get_blockchain().to_pickle(filename="blockschain.pkl")
                # files = {'blockchain_file': open(f"pickles/blockchain.pkl",'rb')}
                files = {'blockchain_file' : pickle.dumps(blkchain)}
                response = requests.post(url, files=files)

    def broadcast_initial_transactions(self):
        for other_node in self.ring_dict.values():
            if other_node['id'] != self.id:
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_initial_transactions'
                files = {'initial_transactions_file': pickle.dumps(self.transaction_pool)}
                response = requests.post(url, files=files)


    def set_ring_dict(self, ring):
        self.ring_dict = ring


    #---Normal Class Functions---
    def set_id(self, id):
        self.id = id

    def get_id_count(self):
        return self.current_id_count	

    def inc_id_count(self):
        self.current_id_count += 1

    def get_my_public_key_tuple(self):
        return self.wallet.get_public_key_tuple()

    def get_UTXOs(self, pubkey):
        return self.UTXOs[pubkey]

    def set_UTXOs(self, id, nbcList):
        self.UTXOs[id] = nbcList

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

    def get_pubkey_by_id(self, id):
        for key in self.ring_dict.keys():
            if self.ring_dict[key]['id'] == id:
                return key

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
        # self.ring.append(new_node)
        self.ring_dict[(n,e)] = new_node

    def mine(self,):
        while True:
            # print("Checking if we need to start mining...")
            self.current_block_lock.acquire()
            # fill up the current block
            while not self.current_block.is_filled():
                if len(self.transaction_pool):
                    # if we have unused transactions put one of them to the block
                    t = self.transaction_pool.pop()
                    self.current_block.add_transaction(t)
                else:
                    # take a short nap waiting for new transactions
                    time.sleep(0.1)
            self.mine_block()
            # print("current transaction pool:", self.transaction_pool)
            self.current_block_lock.release()
            print()
            print(colored("--Completed a new block--", "red"))
            print()
            print(colored(f"current length of the blockchain: {len(self.blockchain.get_chain())}", 'red'))
            print()
            print(colored("--End Completed a new block--", 'red'))
            print()

            time.sleep(0.1)

    def start_mining(self):
        t = Thread(target=self.mine)
        t.start()
        return


    def update_balance(self, public_key, amount):
        node_obj = self.ring_dict[public_key]
        node_obj['balance'] += amount
        self.ring_dict[public_key] = node_obj


    # def create_transaction(sender_address, receiver_address, signature):
    def create_transaction(self, sender_address, receiver_address, private_key,value,do_broadcast=True):
        #remember to broadcast it
        self.UTXO_lock.acquire()
        self.balances_lock.acquire()
        self.transaction_pool_lock.acquire()

        # self.UTXO_lock.release()
        # self.balances_lock.release()
        # self.transaction_pool_lock.release()

        #check if we have enough money
        if self.ring_dict[sender_address]['balance'] < value:
            print("there is not enough money for this transaction")
            self.UTXO_lock.release()
            self.balances_lock.release()
            self.transaction_pool_lock.release()
            return False

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

        # update balances

        self.update_balance(sender_address, -value)
        self.update_balance(receiver_address, value)

        self.transaction_pool.appendleft(trans)

        self.UTXO_lock.release()
        self.balances_lock.release()
        self.transaction_pool_lock.release()

        # broadcast
        if do_broadcast:
            self.broadcast_transaction(trans)

        return True


    def broadcast_transaction(self, the_transaction:Transaction):
        """
        broadcast a new transaction crafted by this node
        """
        for other_node in self.ring_dict.values():
            if other_node['id'] != self.id:
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_transaction'
                files = {'transaction_file' : pickle.dumps(the_transaction)}
                response = requests.post(url, files=files)



    def verify_signature(self, received_transaction:Transaction):
        #use of signature and NBCs balance
        # check signature
        trans_dict = received_transaction.to_dict()
        # signer object
        (n,e) = trans_dict['sender_address']
        singer = PKCS1_v1_5.new(self.get_key_from_tuple(n,e))
        # hash object
        hash_digest = trans_dict["transaction_id"]
        # transaction as dict
        d = {
                "sender_address": received_transaction.sender_address,
                "receiver_address": received_transaction.receiver_address,
                "amount": received_transaction.amount,
                "transaction_inputs": received_transaction.transaction_inputs
                }
        # transaction to hash
        hash_object = SHA.new(data=binascii.a2b_qp(str(d)))
        #signature
        signature = trans_dict["signature"]

        # verify
        try:
            singer.verify(hash_object, signature=signature)
            if hash_digest == hash_object.digest():
                # print("Succesful Verification")
                return True
            else:
                print("Problem Verifying")
                return False
        except:
            print("Problem Verifying")
            return False


    # def update_UTXOs(self, sender, transaction_inputs, transaction_outputs):
    #     self.UTXOs[sender] = list(set(self.UTXOs[sender]).difference(set(transaction_inputs)))
    #     for output in transaction_outputs:
    #         receiver = output['receiver_address']
    #         self.UTXOs[receiver] = self.UTXOs['receiver'].append(output)


    def validate_transaction(self, received_transaction: Transaction):
        self.UTXO_lock.acquire()
        self.balances_lock.acquire()
        self.transaction_pool_lock.acquire()

        if not self.verify_signature(received_transaction=received_transaction):
            self.UTXO_lock.release()
            self.balances_lock.release()
            self.transaction_pool_lock.release()
            return False

        # check NBCs balance
        trans_dict = received_transaction.to_dict()

        trans_inputs = trans_dict["transaction_inputs"]
        sender = trans_dict["sender_address"]
        for item in trans_inputs:
            if item not in self.get_UTXOs(sender):
                self.UTXO_lock.release()
                self.balances_lock.release()
                self.transaction_pool_lock.release()
                return False

        # update UTXOs 
        senderUTXOs = self.UTXOs[sender]
        senderUTXOs = [u for u in senderUTXOs if u not in trans_dict["transaction_inputs"]]
        self.UTXOs[sender] = senderUTXOs

        for output in trans_dict["transaction_outputs"]:
            receiver = output['receiver_address']
            self.UTXOs[receiver].append(output)

        #update balances
        self.update_balance(trans_dict["sender_address"], -trans_dict["amount"])
        self.update_balance(trans_dict["receiver_address"], trans_dict["amount"])


        
        self.transaction_pool.appendleft(received_transaction)
        

        self.UTXO_lock.release()
        self.balances_lock.release()
        self.transaction_pool_lock.release()

    def add_transaction_to_block(self, trans: Transaction):
        try:
            self.current_block.add_transaction(trans)
        except:
            pass

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
        nonce = random.randint(0,1000000)
        self.current_block.set_nonce(nonce=nonce)
        while str(self.current_block.hash)[:difficulty] != proof:
            #TODO add check if another block is received AND validated to stop mining


            self.current_block.nonce += 1
            #hash string
            #hash1 = hashlib.sha256(whole_str.encode()).hexdigest()
            self.current_block.calc_hash()

            #nonce found for required proof

            # self.broadcast_block(self.current_block)
        self.blockchain.add_block(self.current_block)
        previousHash = self.current_block.hash
        new_ind = self.blockchain.get_length()
        self.current_block = block.Block(index=new_ind, previousHash=previousHash)




    def broadcast_block(self, the_block:block.Block):
        """
        broadcast a new block mined by this node
        """
        for other_node in self.ring_dict.values():
            if other_node['id'] != self.id:
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_block'
                files = {'block_file' : pickle.dumps(the_block)}
                response = requests.post(url, files=files)



    def validate_block(self, the_block:block.Block):
        if not self.blockchain.block_exists(the_block.index - 1):
            return False
        if self.blockchain.get_block_hash(the_block.index - 1) != the_block.previousHash:
            return False

        difficulty = self.blockchain.get_difficulty()
        if the_block.hash[:difficulty] != '0'*difficulty:
            return False

        #may need to reconstruct a block to make sure calc_hash() function is correct
        new_block = block.Block(the_block.index, the_block.previousHash, the_block.capacity, the_block.timestamp)
        new_block.set_nonce(the_block.get_nonce())
        new_block.set_transactions(the_block.get_transactions())
        new_block.calc_hash()
        if the_block.hash != new_block.hash:
            return False

        #otherwise just recalculate it
        """
        current_block_hash = the_block.hash
        the_block.calc_hash()
        if the_block.hash != current_block_hash:
            return False
        """

        #individual transaction validation
        for tr in the_block.get_transactions():
            """
            if not self.validate_transaction(tr):   #modify function to not do the transaction so it doesn't happen twice
                return false
            """
            pass

        return True


    # def valid_proof(.., difficulty=MINING_DIFFICULTY):
    # 	pass


    # #concencus functions

    # def valid_chain(self, chain):
    # 	#check for the longer chain accroose all nodes
    # 	pass


    # def resolve_conflicts(self):
    # 	#resolve correct chain
    # 	pass



