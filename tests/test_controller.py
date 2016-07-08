import unittest

from publication import controller


class TestController(unittest.TestCase):

    def test_construct_aggs(self):
        aggs = controller.construct_aggs(['subject_areas'])

        expected = {
            "aggs": {
                "subject_areas": {
                    "terms": {
                        "field": "subject_areas",
                        "size": 0
                    }
                }
            }
        }

        self.assertEqual(expected, aggs)

    def test_construct_aggs_multi_aggs(self):
        aggs = controller.construct_aggs(['collection', 'subject_areas'])

        expected = {
            "aggs": {
                "collection": {
                    "terms": {
                        "field": "collection",
                        "size": 0
                    },
                    "aggs": {
                        "subject_areas": {
                            "terms": {
                                "field": "subject_areas",
                                "size": 0
                            }
                        }
                    }
                }
            }
        }

        self.assertEqual(expected, aggs)
