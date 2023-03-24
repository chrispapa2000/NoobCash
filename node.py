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
from threading import Event


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

        self.miningThread = None
        self.event = Event()

        self.blockchain = Blockchain()

        self.transaction_pool = deque() 

        self.do_mining = False

        self.current_block = block.Block(index=None, previousHash=None)

        self.transaction_count = 0

        self.history = []

        self.block_times = []

        self.last_block_time = time.time()

        # locks
        self.miner_lock = Lock()
        self.foreign_block_lock = Lock()
        self.transaction_pool_lock = Lock()
        self.blockchain_lock = Lock()
        # self.current_block_lock = Lock()
        self.balances_lock = Lock() 
        self.UTXO_lock = Lock()

    #---Initialization Functions---

    # function used by non bootstrap nodes to request participation in the blockchain
    def request_participation(self):
        # if you are not the bootstrap server, you request participation from the bootstrap server
        # make a get request

        # bootstrap_url = 'http://10.0.0.1:5000'
        bootstrap_url = 'http://127.0.0.1:5000'

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
        genesis_block.add_transaction(t0.to_dict())
        genesis_block.set_nonce(0)

        # add the genesis block to the blockchain
        self.blockchain.add_block(genesis_block)

        self.current_block = block.Block(index=1, previousHash=genesis_block.hash)

        self.UTXOs[self.get_my_public_key_tuple()] = [{"transaction_id":0, "receiver_address":self.get_my_public_key_tuple(), "amount":100*self.number_of_nodes}]
        self.history.append(t0.to_dict())

    # function that broadcast info gathered by the bootstrap node to all other nodes
    def broadcast_participants(self):
        # get all pub key files names 
        files = dict()
        files["ring"]=pickle.dumps(self.ring_dict) 

        for other_node in self.ring_dict.values():
            if other_node['id'] != self.id:
                print(other_node)
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_participants_info'
                response = requests.post(url, files=files)

    # function that broadcasts the initial blockhain from the bootstrap node to the other nodes 
    def broadcast_blockchain(self):
        for other_node in self.ring_dict.values():
            if other_node['id'] != self.id:
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_initial_blockchain'
                blkchain = self.get_blockchain()
                files = {'blockchain_file' : pickle.dumps(blkchain)}
                response = requests.post(url, files=files)

    def broadcast_initial_transactions(self):
        for other_node in self.ring_dict.values():
            if other_node['id'] != self.id:
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_initial_transactions'
                files = {'initial_transactions_file': pickle.dumps(self.transaction_pool)}
                response = requests.post(url, files=files)

    def send_mining_start_request(self, url):
        response = requests.get(url)

    def notify_to_start_mining(self):
        for other_node in self.ring_dict.values():
            # if other_node['id'] != self.id:
            if True:
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/start_mining'
                t = Thread(target=self.send_mining_start_request, args=(url,))
                t.start()

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

    def empty_block(self):
        for t_dict in self.current_block.get_transactions():
            self.transaction_pool.appendleft(t_dict)

    def create_new_block(self, previousHash):
        # initialized next block
        new_ind = None
        with self.blockchain_lock:  
            if not previousHash:
                previousHash = self.blockchain.get_block_hash(block_index=-1)
            new_ind = self.blockchain.get_length()
        self.current_block = block.Block(index=new_ind, previousHash=previousHash)

        # fill it up with transactions
        with self.transaction_pool_lock:
            start_time = time.time()
            while not self.current_block.is_filled():
                if len(self.transaction_pool):
                    # if we have unused transactions put one of them to the block
                    t_dict = self.transaction_pool.pop()
                    self.add_transaction_to_block(t_dict)
                else:
                    # take a short nap waiting for new transactions
                    if (time.time()-start_time) > 5:
                        self.empty_block()
                        return False
                    time.sleep(0.1)

        return True

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
        self.ring_dict[(n,e)] = new_node

    def mine(self,):
        while True:
            # self.current_block_lock.acquire()
            # fill up the current block
            self.current_block_lock.acquire()
            while not self.current_block.is_filled():
                if len(self.transaction_pool) >= 0:
                    # if we have unused transactions put one of them to the block
                    t = self.transaction_pool.pop()
                    self.add_transaction_to_block(t)
                else:
                    # take a short nap waiting for new transactions
                    time.sleep(0.1)
            self.current_block_lock.release()
            self.do_mining = True
            self.evemt.clear()
            self.mine_block()

            time.sleep(0.1)

    def check_mining(self):
        while True:
            if not self.miningThread.is_alive():
                self.miningThread = Thread(target=self.mine_block)
                self.miningThread.start()
            time.sleep(0.5)

    def start_mining(self):
        self.miningThread = Thread(target=self.mine_block, args=(0,))
        time.sleep(1)
        self.last_block_time = time.time()
        self.miningThread.start()
        t = Thread(target=self.check_mining)
        t.start()

        return


    def update_balance(self, public_key, amount):
        node_obj = self.ring_dict[public_key]
        node_obj['balance'] += amount
        self.ring_dict[public_key] = node_obj


    # def create_transaction(sender_address, receiver_address, signature):
    def create_transaction(self, sender_address, receiver_address, private_key,value,do_broadcast=True):
        #remember to broadcast it
        print("a")
        self.UTXO_lock.acquire()
        self.balances_lock.acquire()
        self.transaction_pool_lock.acquire()

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


        # update balances
        self.update_balance(sender_address, -value)
        self.update_balance(receiver_address, value)

        self.transaction_pool.appendleft(trans.to_dict())

        self.transaction_count+=1

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



        self.transaction_pool.appendleft(trans_dict)
        self.transaction_count+=1   

        self.UTXO_lock.release()
        self.balances_lock.release()
        self.transaction_pool_lock.release()
        
        return True

    def add_transaction_to_block(self, transaction_dict: dict):
        self.current_block.add_transaction(transaction_dict)     

    def mine_block(self, previousHash=None):
        new_block_found = False
        with self.miner_lock:
            # fill up the block            
            bool_val = self.create_new_block(previousHash=previousHash)
            if not bool_val:
                # not enough transactions to mine rn
                return
            start_time = time.time()

            difficulty = self.blockchain.get_difficulty()
            proof  = '0'*difficulty
            nonce = random.randint(0,1000000)
            self.current_block.set_nonce(nonce=nonce)
            self.current_block.calc_hash()


            # mine to find the correct nonce
            while str(self.current_block.hash)[:difficulty] != proof:
                if self.foreign_block_lock.locked():
                    # empty block and return
                    self.transaction_pool_lock.acquire()
                    for t_dict in self.current_block.get_transactions():
                        self.transaction_pool.appendleft(t_dict)
                    self.transaction_pool_lock.release()
                    return

                self.current_block.nonce += 1
                self.current_block.calc_hash()


            self.blockchain_lock.acquire()

            if self.validate_block(self.current_block):
                self.blockchain.add_block(self.current_block)
                new_block_found = True
                end_time = time.time()
                self.current_block.difficulty = difficulty

                for t_dict in self.current_block.get_transactions():
                    t = Transaction(sender_address=None, sender_private_key=None, recipient_address=None, value=None, 
                                                    transaction_inputs=None, init_dict=t_dict)
                    self.history.append(t)
                self.block_times.append(end_time-start_time) #-self.last_block_time)
                self.last_block_time = end_time
                # print about the new block
                print()
                print(colored("--Completed a new block--", "red"))
                print()
                print(colored(f"current length of the blockchain: {len(self.blockchain.get_chain())}", 'red'))
                print()
                print(colored(f"running average of block time for this node: {sum(self.block_times)/len(self.block_times)}", 'red'))
                print()
                print(colored("--End Completed a new block--", 'red'))
                print()
                file = open(f"chain{self.id}.pkl", 'wb')
                pickle.dump(self.blockchain.get_chain(), file)
                file.close()

                # broadcast the block after clearing the event
                self.event.clear()
                t = Thread(target=self.broadcast_block, args=(self.current_block,))
                t.start()
            else:
                self.transaction_pool_lock.acquire()

                # put some transactions back in the pool
                for t_dict in self.current_block.get_transactions():
                    if t_dict not in self.history:
                        self.transaction_pool.appendleft(t_dict)

                self.transaction_pool_lock.release()

            self.blockchain_lock.release()   
        if new_block_found:
            # if you found the new block wait for the broadcasting thread to signal
            self.event.wait()
            time.sleep(1)
        self.miningThread = Thread(target=self.mine_block)
        self.miningThread.start()

    def broadcast_block(self, the_block:block.Block):
        """
        broadcast a new block mined by this node
        """
        for other_node in self.ring_dict.values():
            if other_node['id'] != self.id:
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_block'
                files = {'block_file' : pickle.dumps(the_block)}
                response = requests.post(url, files=files)
        time.sleep(1)
        self.event.set()


    def validate_block(self, the_block:block.Block):
        if not self.blockchain.block_exists(the_block.index - 1):
            return False
        if self.blockchain.get_block_hash(-1) != the_block.previousHash:
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

    def on_new_block_arrival(self, the_block:block.Block):
        with self.foreign_block_lock:
            with self.miner_lock:
                with self.blockchain_lock:                
                    print()
                    print(colored("Received a foreign block", 'light_magenta'))

                    if self.validate_block(the_block=the_block):
                        self.transaction_pool_lock.acquire()
                        
                        received_block_transactions = the_block.get_transactions() 

                        flag = True
                        for t_dict in received_block_transactions:
                            if not (t_dict in self.transaction_pool):
                                flag = False
                                break
                        if flag:
                            self.blockchain.add_block(the_block)
                            for t_dict in received_block_transactions:
                                self.transaction_pool.remove(t_dict)
                                self.history.append(t_dict)

                        self.transaction_pool_lock.release()

                        print()
                        print(colored("--Received valid block--", 'light_magenta'))
                        print()
                        print(colored(f"--Length of current Blockchain: {self.blockchain.get_length()}--", 'light_magenta'))
                        print()
                        print(colored("--End Received valid block--", 'light_magenta'))
                        print()

                        file = open(f"chain{self.id}.pkl", 'wb')
                        pickle.dump(self.blockchain.get_chain(), file)
                    else:
                        # the block is not valid
                        self.resolve_conflicts()



    def request_chain_lengths(self):
        #max_len = self.blockchain.get_length()
        #best_node = self
        lengths_list = []
        for other_node in self.ring_dict.values():
            if other_node['id'] != self.id:
                url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_chain_length'
                response = requests.get(url)
                response_json = response.json()
                print(response_json['length'])
                length = response_json['length']
                lengths_list.append((other_node,length))
        
        res = sorted(lengths_list, key = lambda x: x[1])
        res.reverse()
        return res

    def request_chain(self, other_node):
        url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_blockchain'
        response = requests.get(url)
        new_blockchain = pickle.loads(response.content)
        return new_blockchain

    def get_longest_valid_chain(self):
        lengths = self.request_chain_lengths()
        best_chain = self.blockchain, "me"
        current_length = self.blockchain.get_length()
        for (other_node, length) in lengths:
            if length <= current_length: #self.blockchain is the longest valid chain
                return self.blockchain, "me"
            candidate_chain = self.request_chain(other_node)
            if self.validate_chain(candidate_chain):
                return candidate_chain, other_node

        return self.blockchain, "me"  #if all others are invalid
            
    # #concencus functions

    def validate_chain(self, chain: Blockchain):
        #check for the longer chain across all nodes
        blocks = chain.get_chain()
        for i in range(1,len(blocks)):
            current_block_dict = blocks[i]
            prev_block_dict = blocks[i-1]
            if current_block_dict['previousHash'] != prev_block_dict['hash']:
                return False

            #may need to reconstruct a block to make sure calc_hash() function is correct
            new_block = block.Block(current_block_dict['index'], previousHash=current_block_dict['previousHash'], capacity=current_block_dict['capacity'],
                                    timestamp=current_block_dict['timestamp'])
            new_block.set_nonce(current_block_dict['nonce'])
            new_block.set_transactions(current_block_dict['listOfTransactions'])
            new_block.calc_hash()
            if current_block_dict['hash'] != new_block.hash:
                return False

            current_chain_transactions = []
            for bl in self.blockchain.get_chain():
                for t_dict in bl['listOfTransactions']:
                    current_chain_transactions.append(t_dict)

            # check if we have seen all the transactions
            with self.transaction_pool_lock:
                current_transaction_pool = [t_dict for t_dict in self.transaction_pool]
                current_known_transactions = current_transaction_pool + current_chain_transactions
                for t_dict in current_block_dict['listOfTransactions']:
                    if t_dict not in current_known_transactions:
                        return False
        return True

    def filter_transactions(self, new_chain:Blockchain):
        # already have miner_lock and blockchain_lock
        current_chain = self.blockchain
        new_chain_transactions, current_chain_transactions = [], []
        for bl in new_chain.get_chain():
            for t_dict in bl['listOfTransactions']:
                new_chain_transactions.append(t_dict)

        # current_chain_transactions = self.history

        for bl in current_chain.get_chain():
            for t_dict in bl['listOfTransactions']:
                current_chain_transactions.append(t_dict)

        with self.transaction_pool_lock:
            transactions_in_pool = [t_dict for t_dict in self.transaction_pool]
            current_transactions_all = transactions_in_pool + current_chain_transactions
            new_transactions_pool = [t_dict for t_dict in current_transactions_all if t_dict not in new_chain_transactions]
            self.transaction_pool = deque(new_transactions_pool)        
            self.history = new_chain_transactions      
        


    def resolve_conflicts(self):
        # resolve correct chain
        # get longest chain
        new_chain, who = self.get_longest_valid_chain()
        print()
        print(colored("--Received invalid block--", 'light_magenta'))
        print()
        print(colored(f"--longest valid Blockchain belongs to {'me' if who=='me' else who['id']}, with length {new_chain.get_length()}--", 'light_magenta'))
        print()
        print(colored("--End Received invalid block--", 'light_magenta'))
        print()
        #adopt chain
        if who == 'me':
            return
                
        # proccess transactions(oof)
        self.filter_transactions(new_chain=new_chain)
        
        self.blockchain = new_chain

        print()
        print(colored("--Received invalid block--", 'light_magenta'))
        print()
        print(colored(f"--Replaced my chain with {'me' if who=='me' else who['id']}'s, with length {new_chain.get_length()}--", 'light_magenta'))
        print()
        print(colored("--End Received invalid block--", 'light_magenta'))
        print()

        

