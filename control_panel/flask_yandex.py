import os

import json
from flask import Flask, request, Response
from mysql.connector import connect
from dotenv import load_dotenv
from functions import load_config_file

app = Flask(__name__)
load_dotenv()

connection = connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)
cur = connection.cursor(dictionary=True)
connection.autocommit = True


def insert_topic(data):
    user_access_code = data['Код подключения']
    true_access_code = load_config_file('config.json')['upload_topic_access_code']
    topic_list = [(a,) for a in data['Список тем'].split('\n') if a.strip()]
    if user_access_code == true_access_code:
        sql_query = "INSERT INTO topic (description) VALUES (%s)"
        cur.executemany(sql_query, topic_list)


@app.route('/uploadtopic', methods=['POST'])
def upload_topic():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        insert_topic(data)
        return "ok"


@app.route('/check', methods=['GET'])
def check_status():
    if request.method == 'GET':
        if connection.is_connected():
            return Response('OK', status=200)
        else:
            return Response('CONNECTION_ERR', status=503)


if __name__ == '__main__':
    app.run()
