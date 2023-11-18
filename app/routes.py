import json
import traceback
from functools import wraps

import pandas as pd
from flask import Response, request
from flask_restx import Resource

from app import api
from app.database import Database

assignment_api = api.namespace('', description='사전 과제 API')


def as_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        res = f(*args, **kwargs)
        res = json.dumps(res, ensure_ascii=False).encode('utf8')
        return Response(res, content_type='application/json; charset=utf-8')

    return decorated_function


@assignment_api.route('/read/<int:id>')
class Read(Resource):
    @as_json
    def get(self, id):
        response = {
            'success': False,
        }
        try:
            result = Database.read('user', id);
            if len(result) == 0:
                response.update({
                    'reason': 'Not Exist.',
                })
            else:
                response.update({
                    'success': True,
                    'data': result[0]
                })
        except Exception as e:
            traceback.print_exc()
            response.update({
                'reason': type(e).__name__,
            })
        return response


@assignment_api.route('/create')
class Create(Resource):
    @as_json
    def post(self):
        response = {
            'success': False,
        }
        data = request.json.get('data')
        # data = [
        #     {"created": datetime(2023, 1, 1, 12, 0, 0), "name": "John", "content": b'something'},
        #     {"created": datetime(2023, 1, 2, 12, 0, 0), "name": "Alice", "content": b'anything'},
        # ]

        try:
            Database.write_bulk('user', pd.DataFrame.from_dict(data=data, orient='columns'))
            response.update({
                'success': True
            })
        except Exception as e:
            traceback.print_exc()
            response.update({
                'reason': type(e).__name__,
            })
        return response


@assignment_api.route('/delete/<int:id>')
class Create(Resource):
    @as_json
    def delete(self, id):
        response = {
            'success': False,
        }

        try:
            Database.delete('user', id)
            response.update({
                'success': True
            })
        except Exception as e:
            traceback.print_exc()
            response.update({
                'reason': type(e).__name__,
            })
        return response

# @assignment_api.get('/insert_test')
# def insert_test():
#     # print(Remote.getShops())
#     values = [];
