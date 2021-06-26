import requests
import sys
import os
import urllib3
# Our dodgy self-signed certificate doesn't have Subject Alt Names. I don't need to know that every time urllib3, thanks
urllib3.disable_warnings()
tls_cert = os.path.join('.','API','certs','nginx-selfsigned.crt')

# Allow the user to pick the number of records
if len(sys.argv) > 1:
    n = int(sys.argv[1])
else:
    n = 20

results = requests.get(f'https://localhost/api/top-authors/{n}', verify=tls_cert).json()

print(' <author> :: <average_rating> ::: <rating_count>')
print('*************************************************')
for row in results:
    print(row['author'], '::', row['average_rating'], ':::', row['rating_count'])
