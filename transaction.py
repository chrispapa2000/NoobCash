from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):


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

        # transaction as dict
        d = {
            "sender_address": self.sender_address,
            "receiver_address": self.receiver_address,
            "amount": self.amount
        }
        # transaction to hash
        hash_object = SHA.new(data=binascii.a2b_qp(jsonify(d)))
        # get the signature
        signer = PKCS1_v1_5.new(sender_private_key)
        #sign the hash object
        signature = signer.sing(hash_object)

        # assign the values 
        self.transaction_id = hash_object
        self.signature = signature

        self.transaction_inputs = [{"previousOutputId":1}] # to be changed
        self.transaction_outputs = [{"transaction_id":1, "receiver_address":1, "amount":1}] # to be changed    


    def to_dict(self):
        d = {
            "sender_address": self.sender_address,
            "receiver_address": self.receiver_address,
            "amount": self.amount
        }
        return d
        

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        pass
       