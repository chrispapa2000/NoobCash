import block
import transaction
from Crypto.PublicKey import RSA
import json
import binascii
import pickle
import os

class Blockchain():
    def __init__(self, block_capacity=1, difficulty=5):
        # initialize the list of blocks
        self.list_of_blocks = []
        self.block_capacity = block_capacity
        self.difficulty = difficulty

    def get_difficulty(self):
        return self.difficulty

    def set_difficulty(self, dif):
        self.difficulty = dif

    def add_block(self, bl: block.Block):
        self.list_of_blocks.append(bl.to_dict())

    def get_block_capacity(self):
        return self.block_capacity
    
    def get_length(self):
        return len(self.list_of_blocks)
    
    def get_chain(self):
        return self.list_of_blocks[:]
    
    def set_chain(self, chain):
        self.list_of_blocks = [blk for blk in chain]


    def to_pickle(self, filename, basedir='pickles'):
            with open(f"{basedir}/{filename}", 'wb') as f:  # open a text file
                pickle.dump(self, f) # serialize the class 

    def from_pickle(self, filename, basedir='pickles'):
        # open pickle file and read it
        with open(f"{basedir}/{filename}", 'rb') as f:
            temp = pickle.load(f)
        
        # transfer the data to current object 
        self.list_of_blocks = temp.list_of_blocks
        self.block_capacity = temp.block_capacity
        
        # # delete .pickle file
        # os.remove(filename)
    
    def block_exists(self, block_index):
        return len(self.list_of_blocks) > block_index

    def get_block_hash(self, block_index):
        if not self.block_exists(block_index):
            raise Exception("Block doesn't exist on blockchain!")
        return self.list_of_blocks[block_index]['hash']


# testing

def main():
    blk = Blockchain()
    b0 = block.Block(0, 0, 2)
    key0= RSA.generate(2048)
    key1= RSA.generate(2048)
    t0 = transaction.Transaction((key0.n,key0.e), key0, (key1.n,key1.e),value=1,transaction_inputs=[{"transaction_id":1, "receiver_address":(key0.n,key0.e), "amount":1}])
    b0.add_transaction(t0)
    t1 = transaction.Transaction((key1.n,key1.e), key1, (key0.n,key0.e),value=5,transaction_inputs=[{"transaction_id":4, "receiver_address":(key1.n,key1.e), "amount":10}])
    b0.add_transaction(t1)
    blk.add_block(b0)
    
    blk.to_pickle(filename="blockchain.pkl")

    blk1 = Blockchain()
    blk1.from_pickle(filename="blockchain.pkl")
    for item in blk1.get_chain():
        print(item)
        print()

    print()
    print(blk.get_chain() == blk1.get_chain())

if __name__=='__main__':
    main()
