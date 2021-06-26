import unittest
from commands import combined_average

class TestCommands(unittest.TestCase):
    def test_combined_average(self):
        # Basic correctness
        rating, count = combined_average(1.0, 1, 2.0, 1)
        self.assertTrue(rating == 1.5)
        self.assertTrue(count == 2) 
        # Zero
        rating, count = combined_average(0, 0, 0, 0)
        self.assertTrue(rating == 0)
        self.assertTrue(count == 0) 
        # Zero2
        rating, count = combined_average(10.0, 0, 0.0, 10)
        self.assertTrue(rating == 0)
        self.assertTrue(count == 10) 
        # Sneaky string
        rating, count = combined_average('1', 1, 2, 1)
        self.assertTrue(rating == 1.5)
        self.assertTrue(count == 2) 
        # Negative data
        # We're handling the data in a mathematically true way
        # i.e. (-1 + 2) / 2 = 0.5, a perfectly cromulent average
        rating, count = combined_average(-1.0, 1, 2.0, 1)
        self.assertTrue(rating == 0.5)
        self.assertTrue(count == 2)        
        # We avoid the divide by zero problem by automatically giving 
        # zero ratings an average of zero (this is technically a stand-in for undefined)
        rating, count = combined_average(-1.0, 1, 2.0, -1)
        self.assertTrue(rating == 0.0)
        self.assertTrue(count == 0)        
        # This doesn't make a whole lot of sense but it mathematically consistent
        # i.e. (-1 + -4) / -1 = 5.0
        # We may want to put a guard on against negative counts or ratings but 
        # this should really be the reponsibility of the data ingress service 
        # so we can keep the inner loop logic lean.
        rating, count = combined_average(-1.0, 1, 2.0, -2)
        print(rating, count)
        self.assertTrue(rating == 5.0)
        self.assertTrue(count == -1)        

if __name__ == '__main__':
    unittest.main()
