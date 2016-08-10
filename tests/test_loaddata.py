# coding: utf-8
import unittest

from processing import loaddata


class TestLoadData(unittest.TestCase):

    def test_country_1(self):

        result = loaddata.country('Brazil')

        self.assertEqual(result, 'BR')

    def test_country_2(self):

        result = loaddata.country('Br')

        self.assertEqual(result, 'BR')

    def test_state_1(self):

        result = loaddata.state('SP', 'BR')

        self.assertEqual(result, 'BR-SP')

    def test_state_2(self):

        result = loaddata.state('São Paulo', 'BR')

        self.assertEqual(result, 'BR-SP')
