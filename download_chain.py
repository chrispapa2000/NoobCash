import requests
import flask
from blockchain import Blockchain 
import pickle

def main():
    # url = 'http://localhost:5000/get_blockchain'
    # response = requests.get(url)

    # # print(response.headers)

    # b = Blockchain()
    # b = pickle.loads(response.content)
    # print(b.get_chain())

    b0 = Blockchain()
    b1 = Blockchain()
    f = open('chain0.pkl', 'rb')
    b0.set_chain(pickle.load(f))
    f = open('chain1.pkl', 'rb')
    b1.set_chain(pickle.load(f))
    for i in range(len(b0.get_chain())):
        print(b0.get_chain()[i]['listOfTransactions']==b1.get_chain()[i]['listOfTransactions'])
        print(b0.get_chain() == b1.get_chain())
    
    for i in range(len(b0.get_chain())):
        print(f"length of block {i}", len(b0.get_chain()[i]['listOfTransactions']))
        print(f"index of block {i}", b0.get_chain()[i]['index'])
    # print(len((b1.get_chain())))



if __name__=='__main__':
    main()