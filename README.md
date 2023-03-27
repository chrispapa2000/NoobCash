# NoobCash

## Set up a Noobcash network with 5 nodes
Start the boostrap node:

    python3 rest.py -b 1 -n 5 -df <mining_difficutly> -bc <block_capacity>

Start 4 other nodes executing the following for each one of them:

    python3 rest.py -df <mining_difficutly> -bc <block_capacity> -p <port>

## Set up a Noobcash network with 10 nodes
Start the boostrap node:

    python3 rest.py -b 1 -n 10 -df <mining_difficutly> -bc <block_capacity>

Start 9 other nodes executing the following for each one of them:

    python3 rest.py -df <mining_difficutly> -bc <block_capacity> -p <port>

## Create a new transaction:

    python3 client.py --action t --node <sender_id> --recipient <recipient_id> --value <transaction_amount>

## View transactions in the last blockchain block of a certain node

    python3 client.py --action view --node <node_id>

## View the current balance of a certain node

    python3 client.py --action balance --node <node_id>