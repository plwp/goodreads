import unittest
import time
import csv
import requests
import urllib3
import os
import sys

# Our dodgy self-signed certificate doesn't have Subject Alt Names. I don't need to know that every time urllib3, thanks
urllib3.disable_warnings()
tls_cert = os.path.join('.','API','certs','nginx-selfsigned.crt')

base_dataset = [
            { 'author':'Mary Shelly', 'title':'Frankenstein', 'average_rating': 5.0, 'rating_count':10 },
            { 'author':'H.P. Lovecraft', 'title': 'The Call Of Cthulu', 'average_rating': 4.0, 'rating_count':5 },
            { 'author':'Mary Shelly', 'title': 'The Last Man', 'average_rating': 4.0, 'rating_count':40 }  
        ]

def send_to_api(data):
    urllib3.disable_warnings()
    requests.post('https://localhost/api/update', verify=tls_cert, json=data)
    time.sleep(5)
    return requests.get(f'https://localhost/api/top-authors/50', verify=tls_cert).json()

## These must be run with a clean database
class TestAPI(unittest.TestCase):
    def test_averaging(self):
        # We're using a single function to ensure linear execution
        # Empty set
        print('Empty set test...')
        processed = send_to_api([])
        self.assertTrue(len(processed) == 0)
    
        # Basic functionality
        print('Basic functionality test...')
        processed = send_to_api(base_dataset)
        self.assertTrue(len(processed) == 2)
        example = [row for row in processed if row['author'] == 'Mary Shelly']
        # We should only have 1 record per author
        self.assertTrue(len(example) == 1)
        self.assertTrue(example[0]['average_rating'] == 4.2)
        self.assertTrue(example[0]['rating_count'] == 50)
            
        # Zero Values
        print('Zero value test...')
        data = [{ 'author':'Mary Shelly', 'title':'Frankenstein', 'average_rating': 5.0, 'rating_count':0 },
            { 'author':'Mary Shelly', 'title':'Frankenstein', 'average_rating': 0, 'rating_count':0 }]
        processed = send_to_api(data)
        example = [row for row in processed if row['author'] == 'Mary Shelly']
        self.assertTrue(example[0]['average_rating'] == 4.2)
        self.assertTrue(example[0]['rating_count'] == 50)
        
        # Non-English Data + Sneaky string
        print('Non-English Data + Sneaky string test...')
        swedish_data = [
            { 'author':'Sonja Åkesson', 'title':'Skvallerspegel', 'average_rating': 4.5, 'rating_count':10 },
            { 'author':'Sonja Åkesson', 'title':'Efter balen ', 'average_rating': '4', 'rating_count':10 }
        ]
        processed = send_to_api(swedish_data)
        example = [row for row in processed if row['author'] == 'Sonja Åkesson']
        self.assertTrue(example[0]['average_rating'] == 4.25)
        self.assertTrue(example[0]['rating_count'] == 20)
        # Check that the unicode name was preserved
        self.assertTrue(example[0]['author'] == 'Sonja Åkesson')
        
        # We're not giving feedback for failed data (let's say for security)
        # But bad data should be reflected in the results.
        print('Malformed data test...')
        old_data = processed
        bad_data = [{'authors': 'Somdasda', 'rating': 1, 'count':2.3}]
        processed = send_to_api(bad_data)
        self.assertTrue(len(processed) == len(old_data))      
        self.assertTrue(processed[-1]['rating_count'] == old_data[-1]['rating_count'])      
        bad_data = [{'author': 'Somdasda', 'average_rating': 'not even a number', 'rating_count':2.3}]
        self.assertTrue(len(processed) == len(old_data))      
        self.assertTrue(processed[-1]['rating_count'] == old_data[-1]['rating_count'])      
        processed = send_to_api(bad_data)

if __name__ == '__main__':
    unittest.main()
