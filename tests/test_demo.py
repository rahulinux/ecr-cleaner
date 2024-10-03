import unittest

from template_package import hello_world


class TestSelect(unittest.TestCase):
    def setUp(self):
        self.expected = "hello-world"

    def test_demo(self):
        result = hello_world()
        self.assertEqual(result, self.expected)


if __name__ == "__main__":
    unittest.main()
