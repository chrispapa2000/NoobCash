import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

class wallet:

	def __init__(self):
		# generate an RSA key
		key = RSA.generate(2048)

		# write the key to a file
		f = open('mykey.pem','wb')
		f.write(key.export_key('PEM'))
		f.close()
		
		# keys as class attibutes
		self.public_key = key.public_key()
		self.private_key = key

		#self_address
		#self.transactions

	# def balance():

	def sign(self,data):
		# get the key
		f = open('mykey.pem','r')
		key = RSA.import_key(f.read())
		
		# signature object
		signer = PKCS1_v1_5.new(key)

		# hash object
		hash_object = SHA.new(data=binascii.a2b_qp(data))

		# sign the hash object
		signature = signer.sign(hash_object)
		return signature

	def verify(self, data, signature):
		# get the key
		f = open('mykey.pem','r')
		key = RSA.import_key(f.read())
		key = key.public_key()
		
		# signature object
		singer = PKCS1_v1_5.new(key)

		# hash object
		hash_object = SHA.new(data=binascii.a2b_qp(data))

		# sign the hash object
		try:
			singer.verify(hash_object, signature=signature)
			print("Succesful Verification")
		except:
			print("Problem Verifying")

# testing 

def main():
	w = wallet()
	sig = w.sign("Hello World")
	w.verify("Hello World", sig)

if __name__ == '__main__':
	main()