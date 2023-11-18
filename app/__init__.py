import os

from dotenv import load_dotenv
from flask import Flask
from flask_restx import Api

load_dotenv('../.env')

app = Flask(__name__)
api = Api(app, version='1.0', title='API 문서', description='Swagger 문서', doc="/api-docs")

from app import routes

if __name__ == "__main__":
    # debug=False  >>  코드변경을 감지해 자동으로 리로드 && 문제가 발생하면 문제를 찾을수 있도록 디버거를 제공
    # host='0.0.0.0'  >>  OS에게 모든 public IP를 접근가능도록 설정
    app.run(debug=False, host='0.0.0.0', port=80)
