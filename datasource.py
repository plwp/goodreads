import time
import csv
import requests
import urllib3
import os
import sys

# Our dodgy self-signed certificate doesn't have Subject Alt Names. I don't need to know that every time urllib3, thanks
urllib3.disable_warnings()
tls_cert = os.path.join('.','API','certs','nginx-selfsigned.crt')

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = 'goodreads_books.csv'


print('Loading CSV data...')
with open(filename, encoding="utf-8") as csvfile:
    # Read the csv file.
    rows = [r for r in csv.DictReader(csvfile, quotechar='"')]

    # Upload the data in batches
    old_i = 0
    for i in range(1000, len(rows), 1000):
        print(f'Sending rows {old_i}-{i}...')
        res = requests.post('https://localhost/api/update', verify=tls_cert, json=rows[old_i:i])
        print(res)
        old_i = i
    print(f'Sending rows {old_i}-{len(rows)}')
    res = requests.post('https://localhost/api/update', verify=tls_cert, json=rows[old_i:])
    
    print('Sent')
