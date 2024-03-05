import ipfsapi

# Connect to the local IPFS daemon
api = ipfsapi.Client('127.0.0.1', 5001)

# Add a file to IPFS
res = api.add('abc.txt')
file_hash = res['Hash']
print("File added with hash:", file_hash)
