import json
import logging
import sys
import unittest
from datetime import datetime

import app


# to make order for test
def make_orderer():
    order = {}

    def ordered(f):
        order[f.__name__] = len(order)
        return f

    def compare(a, b):
        return [1, -1][order[a] < order[b]]

    return ordered, compare


ordered, compare = make_orderer()
unittest.defaultTestLoader.sortTestMethodsUsing = compare

# to print something while testing, use logger.info
logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class MyUnitTest(unittest.TestCase):
    def setUp(self):
        self.app = app.app
        self.app.config['TESTING'] = True
        self.app = self.app.test_client()

        self.create_data = [
            {"id": 1004, "created": datetime(2023, 1, 1, 12, 0, 0), "name": "John", "content": "something"},
            {"id": 1005, "created": datetime(2023, 1, 2, 12, 0, 0), "name": "Alice", "content": "anything"},
        ]
        self.update_data = [
            {"id": 1004, "name": "Alice", "content": "something"},
            {"id": 1005, "name": "John", "content": "anything"},
        ]

    @ordered
    def test_create(self):
        response = self.app.post('/create',
                                 data=json.dumps(self.create_data, ensure_ascii=False, default=str),
                                 content_type="application/json")

        data = json.loads(response.get_data())
        self.assertEqual(True, data['success'])

    @ordered
    def test_read(self):
        for item in self.create_data:
            response = self.app.get(f"/read/{item['id']}")
            response_data = json.loads(response.get_data())
            self.assertEqual(True, response_data['success'])
            data = response_data['data']
            for key in item.keys():
                self.assertEqual(parse_string(item[key]), data[key])

    @ordered
    def test_update(self):
        for item in self.update_data:
            response = self.app.put(f"/update/{item['id']}",
                                    data=json.dumps(item, ensure_ascii=False, default=str),
                                    content_type="application/json")
            response_data = json.loads(response.get_data())
            self.assertEqual(True, response_data['success'])

    @ordered
    def test_read_after_update(self):
        for item in self.update_data:
            response = self.app.get(f"/read/{item['id']}")
            response_data = json.loads(response.get_data())
            self.assertEqual(True, response_data['success'])
            data = response_data['data']
            for key in item.keys():
                self.assertEqual(parse_string(item[key]), data[key])

    @ordered
    def test_delete(self):
        for item in self.create_data:
            response = self.app.delete(f"/delete/{item['id']}")
            data = json.loads(response.get_data())
            self.assertEqual(True, data['success'])


# string parser for json result
def parse_string(value):
    if isinstance(value, bytes):
        value = value.decode('utf-8')
    if isinstance(value, bytearray):
        value = bytes(value).decode('utf-8')
    elif isinstance(value, datetime):
        value = value.strftime("%Y-%m-%d, %H:%M:%S")
    return value


if __name__ == '__main__':
    unittest.main()
