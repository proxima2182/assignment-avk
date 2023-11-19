import json
import logging
import sys
import unittest
from datetime import datetime

import app

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class UnitTest(unittest.TestCase):
    def setUp(self):
        self.app = app.app
        self.app.config['TESTING'] = True
        self.app = self.app.test_client()

        self.create_data = [
            {"id": 1004, "created": datetime(2023, 1, 1, 12, 0, 0), "name": "John", "content": b'something'},
            {"id": 1005, "created": datetime(2023, 1, 2, 12, 0, 0), "name": "Alice", "content": b'anything'},
        ]
        self.update_data = [
            {"id": 1004, "name": "Alice", "content": b'something'},
            {"id": 1005, "name": "John", "content": b'anything'},
        ]

    async def test_create(self):
        response = self.app.post('/create',
                                 data=json.dumps(self.create_data, ensure_ascii=False, default=str),
                                 content_type="application/json")

        data = json.loads(response.get_data())
        self.assertEqual(True, data['success'])

    async def test_read(self):
        for item in self.create_data:
            response = self.app.get(f"/read/{item['id']}")
            response_data = json.loads(response.get_data())
            self.assertEqual(True, response_data['success'])
            data = response_data['data']
            for key in item.keys():
                self.assertEqual(item[key], data[key])

    async def test_update(self):
        for item in self.update_data:
            # logger.info(item)
            response_update = self.app.put(f"/update/{item['id']}",
                                           data=json.dumps(item, ensure_ascii=False, default=str),
                                           content_type="application/json")
            response_data_update = json.loads(response_update.get_data())
            self.assertEqual(True, response_data_update['success'])

            response_read = self.app.get(f"/read/{item['id']}")
            response_data_read = json.loads(response_read.get_data())
            self.assertEqual(False, response_data_read['success'])
            data_read = response_data_read['data']
            # logger.info(data_read)
            for key in item.keys():
                self.assertEqual(item[key], data_read[key])

    async def test_delete(self):
        for item in self.create_data:
            response = self.app.delete(f"/delete/{item['id']}")
            data = json.loads(response.get_data())
            self.assertEqual(True, data['success'])


if __name__ == '__main__':
    unittest.main()
