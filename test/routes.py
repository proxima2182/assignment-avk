import unittest

from app import app


class UnitTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    # def test_case_1(self):
    #
    # def test_case_2(self):
    #
    # def tearDown(self):

if __name__ == '__main__':
    unittest.main()