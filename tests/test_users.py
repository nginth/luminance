import unittest
import sys
sys.path.append('..')
from luminance.models import User

class TestUserModel(unittest.TestCase):
    def test_exp_level(self):
        u = User('asdfa', 'asdff', 'asdfas')
        u.exp = 301
        self.assertEqual(u.exp_level, 3)

if __name__ == '__main__':
    unittest.main()

        