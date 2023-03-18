import block
import transaction
from Crypto.PublicKey import RSA
import json
import binascii
import pickle
import os

class Blockchain():
    def __init__(self, block_capacity=5):
        # initialize the list of blocks
        self.list_of_blocks = []
        self.block_capacity = block_capacity

    def add_block(self, bl: block.Block):
        self.list_of_blocks.append(bl.to_dict())

    def get_block_capacity(self):
        return self.block_capacity
    
    def get_chain(self):
        return self.list_of_blocks
    
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


# testing

def main():
    blk = Blockchain()
    b0 = block.Block(0, 0, 2)
    
    t0 = transaction.Transaction(0,RSA.generate(2048),2,value=1,transaction_inputs=[{"transaction_id":1, "receiver_address":0, "amount":1}])
    b0.add_transaction(t0)
    t1 = transaction.Transaction(0,RSA.generate(2048),2,value=1,transaction_inputs=[{"transaction_id":5, "receiver_address":0, "amount":5}])
    b0.add_transaction(t1)
    blk.add_block(b0)
    
    blk.to_pickle(filename="blockchain.pkl")

    blk1 = Blockchain()
    blk1.from_pickle(filename="blockchain.pkl")
    print(blk1.get_chain())

    print()
    print(blk.get_chain() == blk1.get_chain())

if __name__=='__main__':
    main()