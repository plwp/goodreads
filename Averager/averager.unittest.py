import unittest
from averager import process_data

base_dataset = [
            { 'author':'Mary Shelly', 'title':'Frankenstein', 'average_rating': 5.0, 'rating_count':10 },
            { 'author':'H.P. Lovecraft', 'title': 'The Call Of Cthulu', 'average_rating': 4.0, 'rating_count':5 },
            { 'author':'Mary Shelly', 'title': 'The Last Man', 'average_rating': 4.0, 'rating_count':40 }  
        ]

class TestAverager(unittest.TestCase):
    def test_process_data(self):
        # We're using a single function to ensure linear execution
        # Basic functionality
        processed = process_data(base_dataset)
        self.assertTrue(len(processed) == 2)
        example = [row for row in processed if row['author'] == 'Mary Shelly']
        # We should only have 1 record per author
        self.assertTrue(len(example) == 1)
        self.assertTrue(example[0]['average_rating'] == 4.2)
        self.assertTrue(example[0]['rating_count'] == 50)
        
        # Empty set
        processed = process_data([])
        self.assertTrue(len(processed) == 0)
        
        # Zero Values
        base_dataset.append({ 'author':'Mary Shelly', 'title':'Frankenstein', 'average_rating': 5.0, 'rating_count':0 })
        base_dataset.append({ 'author':'Mary Shelly', 'title':'Frankenstein', 'average_rating': 0, 'rating_count':0 })
        processed = process_data(base_dataset)
        self.assertTrue(len(processed) == 2)
        example = [row for row in processed if row['author'] == 'Mary Shelly']
        self.assertTrue(len(example) == 1)
        self.assertTrue(example[0]['average_rating'] == 4.2)
        self.assertTrue(example[0]['rating_count'] == 50)
        
        # Non-English Data + Sneaky string
        swedish_data = [
            { 'author':'Sonja Åkesson', 'title':'Skvallerspegel', 'average_rating': 4.5, 'rating_count':10 },
            { 'author':'Sonja Åkesson', 'title':'Efter balen ', 'average_rating': '4', 'rating_count':10 }
        ]
        processed = process_data(swedish_data)
        self.assertTrue(processed[0]['average_rating'] == 4.25)
        self.assertTrue(processed[0]['rating_count'] == 20)
        # Check that the unicode name was preserved
        self.assertTrue(processed[0]['author'] == 'Sonja Åkesson')
        
        # Malformed data will raise an exception, but we can use this pattern to check 
        # that it's the type we expect
        bad_data = [{'authors': 'Somdasda', 'rating': 1, 'count':2.3}]
        with self.assertRaises(KeyError):
            processed = process_data(bad_data)
             
        bad_data = [{'author': 'Somdasda', 'average_rating': 'not even a number', 'rating_count':2.3}]
        with self.assertRaises(ValueError):
            processed = process_data(bad_data)

if __name__ == '__main__':
    unittest.main()
