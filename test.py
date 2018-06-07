import unittest
from target import target


class MyTest(unittest.TestCase):

    def test1(self):
        self.assertEqual(target.fun(3), 4)

    def test2(self):
        self.assertEqual(target.fun2(3), 9)

    def test3(self):
        self.assertEqual(target.fun3(1, 8), 9)
