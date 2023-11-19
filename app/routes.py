import json
import logging
import sys
import traceback
from functools import wraps

import pandas as pd
from flask import Response, request
from flask_restx import Resource, fields

from app import api
from app.database import Database

assignment_api = api.namespace('', description='사전 과제 API')

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


def as_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        res = f(*args, **kwargs)
        res_string = res
        code = 200
        if 'success' not in res and len(res) > 1:
            res_string = res[0]
            code = res[1]
        res_string = json.dumps(res_string, ensure_ascii=False).encode('utf8')
        return Response(res_string, status=code, content_type='application/json; charset=utf-8')

    return decorated_function


api_update_user_fields = api.model('UpdateUser', {
    'created': fields.String(description="DateTime", default="yyyy-MM-dd HH:mm:ss"),
    # 'created': fields.DateTime,
    'name': fields.String(max_length=100, strict=True),
    'content': fields.String,
})
api_user_fields = api.inherit('User', api_update_user_fields, {
    'id': fields.Integer,
})
result_fields = api.model('Result', {
    'success': fields.Boolean(default=True),
    'reason': fields.String(description='optional, appear if (\'success\' = False)'),
})
user_result_fields = api.inherit('UserDataResult', result_fields, {
    'data': fields.Nested(api_user_fields, allow_null=True, description='optional, disappear if (\'success\' = False)'),
})


@assignment_api.route('/read/<int:id>')
@assignment_api.doc(params={'id': 'row id'})
class Read(Resource):
    @api.response(200, 'Success', user_result_fields)
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
    @api.expect([api_user_fields])
    @api.response(200, 'Success', result_fields)
    @as_json
    def post(self):
        response = {
            'success': False,
        }
        data = request.json
        # data = [
        #     {"created": datetime(2023, 1, 1, 12, 0, 0), "name": "John", "content": b'something'},
        #     {"created": datetime(2023, 1, 2, 12, 0, 0), "name": "Alice", "content": b'anything'},
        # ]

        try:
            Database.insert_bulk('user', pd.DataFrame.from_dict(data=data, orient='columns'))
            response.update({
                'success': True
            })
        except Exception as e:
            traceback.print_exc()
            response.update({
                'reason': type(e).__name__,
            })
        return response


@assignment_api.route('/update/<int:id>')
@assignment_api.doc(params={'id': 'row id'})
class Update(Resource):
    @api.expect(api_update_user_fields)
    @api.response(200, 'Success', result_fields)
    @as_json
    def put(self, id):
        response = {
            'success': False,
        }
        data = request.json

        try:
            Database.update("user", id, data)
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
@assignment_api.doc(params={'id': 'row id'})
class Delete(Resource):
    @api.response(200, 'Success', result_fields)
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
