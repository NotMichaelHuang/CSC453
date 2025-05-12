import unittest
from memSim import manage_memory


class MyTestCase(unittest.TestCase):

    def test_fifo1(self):
        out = manage_memory("tests/fifo1.txt", 10, 'fifo')
        self.assertEqual(out[0], 10) # Page Faults
        self.assertEqual(out[1], 10) # TLB Misses

    def test_fifo2(self):
        out = manage_memory("tests/fifo2.txt", 5, 'fifo')
        self.assertEqual(out[0], 10)
        self.assertEqual(out[1], 10)

    def test_fifo3(self):
        out = manage_memory("tests/fifo3.txt", 5, 'fifo')
        self.assertEqual(out[0], 5)
        self.assertEqual(out[1], 5)

    def test_fifo4(self):
        out = manage_memory("tests/fifo4.txt", 5, 'fifo')
        self.assertEqual(out[0], 8)
        self.assertEqual(out[1], 8)

    def test_fifo5(self):
        out = manage_memory("tests/fifo5.txt", 7, 'fifo', 5)
        self.assertEqual(out[0], 11)
        self.assertEqual(out[1], 13)

    def test_lru1(self):
        out = manage_memory("tests/lru1.txt", 5, 'lru')
        self.assertEqual(out[0], 10)
        self.assertEqual(out[1], 10)

    def test_lru2(self):
        out = manage_memory("tests/lru2.txt", 5, 'lru')
        self.assertEqual(out[0], 8)
        self.assertEqual(out[1], 8)

    def test_lru3(self):
        out = manage_memory("tests/lru3.txt", 3, 'lru')
        self.assertEqual(out[0], 7)
        self.assertEqual(out[1], 7)

    def test_opt1(self):
        out = manage_memory("tests/opt1.txt", 5, 'opt')
        self.assertEqual(out[0], 10)
        self.assertEqual(out[1], 10)

    def test_opt2(self):
        out = manage_memory("tests/opt2.txt", 5, 'opt')
        self.assertEqual(out[0], 9)
        self.assertEqual(out[1], 9)

    # test cases based on in-class/quiz examples

    def test_class1_fifo(self):
        out = manage_memory("tests/class1.txt", 3, 'fifo')
        self.assertEqual(out[0], 8)
        self.assertEqual(out[1], 8)

    def test_class1_lru(self):
        out = manage_memory("tests/class1.txt", 3, 'lru')
        self.assertEqual(out[0], 6)
        self.assertEqual(out[1], 6)

    def test_class1_opt(self):
        out = manage_memory("tests/class1.txt", 3, 'opt')
        self.assertEqual(out[0], 6)
        self.assertEqual(out[1], 6)

    def test_class2_fifo(self):
        out = manage_memory("tests/class2.txt", 3, 'fifo')
        self.assertEqual(out[0], 11)
        self.assertEqual(out[1], 11)

    def test_class2_lru(self):
        out = manage_memory("tests/class2.txt", 3, 'lru')
        self.assertEqual(out[0], 13)
        self.assertEqual(out[1], 13)

    def test_class2_opt(self):
        out = manage_memory("tests/class2.txt", 3, 'opt')
        self.assertEqual(out[0], 10)
        self.assertEqual(out[1], 10)


if __name__ == '__main__':
    unittest.main()
