import unittest
from board_class import Board

class BoardClassTestSuit(unittest.TestCase):

    def setUp(self):
        pass

    def test_board_class_creation(self):
        board = Board()
        
        self.assertEqual(True, isinstance(board,Board))
        

class FothelloTestSuit(unittest.TestCase):
    def setUp(self):
        pass       


if __name__ == '__main__':
    unittest.main()
