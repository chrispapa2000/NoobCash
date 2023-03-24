
# import blockchain
import transaction
import time
import pickle
# import json
from Crypto.Hash import SHA256
import hashlib
import random
from Crypto.PublicKey import RSA
import json
from Crypto.Hash import SHA
import binascii





class Block:
    def __init__(self, index, previousHash, capacity=1, timestamp = time.time()):
        ##set
        #self.previousHash
        #self.timestamp
        self.hash = None
        self.nonce = random.randint(1,100) * 100000
        #self.listOfTransactions
        self.index = index
        self.previousHash = previousHash
        self.capacity = capacity
        self.timestamp = timestamp
        self.listOfTransactions = []
        #self.nonce = None
        #self.current_hash = None
        self.difficulty = 1

    def to_dict(self):
        d = {
                "index": self.index,
                "previousHash": self.previousHash,
                "timestamp": self.timestamp,
                "capacity": self.capacity,
                "listOfTransactions": self.listOfTransactions,
                "nonce": self.nonce,
                "hash": self.hash
            }
        return d

    def calc_hash(self):
        #calculate self.hash
        block_list = [self.timestamp, [tr['transaction_id'] for tr in self.listOfTransactions], self.nonce, self.previousHash]
        # print(block_list)
        # return
        # tmp = json.dumps(block_list)
        tmp = str(block_list)
        # self.hash = SHA.new(tmp.encode("ISO-8859-2")).hexdigest()
        # self.hash = SHA.new(data=binascii.a2b_qp(tmp))
        self.hash = hashlib.sha256(tmp.encode()).hexdigest()
        # self.hash = hash(tmp)
        # print(self.hash)

        #self.hash = 1 # to be changed 

    #two blocks are equal if current hash is equal
    def __eq__(self, other):
        return self.current_hash == other.current_hash

    def set_nonce(self, nonce):
        self.nonce = nonce # this maybe has to go on init too? 

    def get_nonce(self):
        return self.nonce

    def get_transactions(self):
        return self.listOfTransactions[:]

    def set_transactions(self, transactions):
        self.listOfTransactions = transactions

    def add_transaction(self, trans_dict, blkchain=None):
        if self.is_filled():
            raise Exception("Block is filled. Adding transaction would exceed capacity.")

        #add a transaction to the block
        self.listOfTransactions.append(trans_dict)

    def is_filled(self):
        return len(self.listOfTransactions) >= self.capacity

    def to_pickle(self, filename, basedir='pickles'):
        with open(f"{basedir}/{filename}", 'wb') as f:  # open a text file
            pickle.dump(self, f) # serialize the class 

    def from_pickle(self, filename, basedir='pickles'):
        # open pickle file and read it
        with open(f"{basedir}/{filename}", 'rb') as f:
            temp = pickle.load(f)

        # transfer the data to current object 
        self.index = temp.index
        self.previousHash = temp.previousHash
        self.capacity = temp.capacity
        self.timestamp = temp.capacity
        self.listOfTransactions = temp.listOfTransactions
        self.hash = temp.hash
        self.nonce = temp.nonce

        # # delete .pickle file
        # os.remove(filename)


if __name__ == "__main__":
    b0 = Block(0, 0, 2)
    key0= RSA.generate(2048)
    key1= RSA.generate(2048)
    t0 = transaction.Transaction((key0.n,key0.e), key0, (key1.n,key1.e),value=1,transaction_inputs=[{"transaction_id":1, "receiver_address":(key0.n,key0.e), "amount":1}])
    b0.add_transaction(t0)
    t1 = transaction.Transaction((key1.n,key1.e), key1, (key0.n,key0.e),value=5,transaction_inputs=[{"transaction_id":4, "receiver_address":(key1.n,key1.e), "amount":10}])
    b0.add_transaction(t1)
    st = time.time()
    nonce = random.randint(1,10000)
    while True:
        nonce+=1
        b0.set_nonce(nonce=nonce)
        b0.calc_hash()
        if str(b0.hash).startswith("00000"):
            break
    print(b0.hash)
    print(time.time()-st)

