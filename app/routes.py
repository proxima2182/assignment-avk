import json
import traceback
from functools import wraps
from json import JSONEncoder

from flask import Response
from flask_restx import Resource

from app import api
from app.database import Database

assignment_api = api.namespace('', description='사전 과제 API')


class MyEncoder(JSONEncoder):
    def default(self, o):
        print(self)
        return o.__dict__


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
            result = Database.read("SELECT * FROM user where id=%s", [id]);
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
            response.update({
                'reason': type(e).__name__,
            })
            traceback.print_exc()
        return response

# @assignment_api.get('/insert_test')
# def insert_test():
#     # print(Remote.getShops())
#     values = [];
