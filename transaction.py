from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template
import json


class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value, transaction_inputs):
        ##set
        #self.sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
        #self.receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        #self.amount: το ποσό που θα μεταφερθεί
        #self.transaction_id: το hash του transaction
        #self.transaction_inputs: λίστα από Transaction Input 
        #self.transaction_outputs: λίστα από Transaction Output 
        #selfSignature

        self.sender_address = sender_address
        self.receiver_address = recipient_address
        self.amount = value


        # self.transaction_inputs = [{"previousOutputId":1}] # to be changed
        # self.transaction_outputs = [{"transaction_id":1, "receiver_address":1, "amount":1}] # to be changed 
        
        # adds the transaction id and signature fields
        # if sender_private_key:
        self.private_key = sender_private_key
        self.sign_transaction()

        self.transaction_inputs = transaction_inputs
        self.set_transaction_outputs()
        
        


    def to_dict(self):
        d = {
            "sender_address": self.sender_address,
            "receiver_address": self.receiver_address,
            "amount": self.amount,
            "transaction_id": self.transaction_id,
            "signature": self.signature,
            "transaction_inputs": self.transaction_inputs,
            "transaction_outputs": self.transaction_outputs
        }
        return d
    

    def set_transaction_outputs(self):
        total = self.amount
        for item in self.transaction_inputs:
            # print(item)
            total -= item['amount']
        # return
        self.transaction_outputs = []
        # output for sender
        self.transaction_outputs.append({"transaction_id":self.transaction_id, "receiver_address":self.sender_address, "amount":-total})
        # outputs for reciever
        self.transaction_outputs.append({"transaction_id":self.transaction_id, "receiver_address":self.receiver_address, "amount":self.amount})

              

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        # transaction as dict
        d = {
            "sender_address": self.sender_address,
            "receiver_address": self.receiver_address,
            "amount": self.amount
        }
        # transaction to hash
        hash_object = SHA.new(data=binascii.a2b_qp(str(d)))
        # get the signature
        signer = PKCS1_v1_5.new(self.private_key)
        #sign the hash object
        signature = signer.sign(hash_object)

        # assign the values 
        self.transaction_id = hash_object
        self.signature = signature



# for testing 
def main():
    t = Transaction(1,RSA.generate(2048),2,1,[{"transaction_id":1, "receiver_address":1, "amount":1}])
    print(t.to_dict())

if __name__=="__main__":
    main()
        
       