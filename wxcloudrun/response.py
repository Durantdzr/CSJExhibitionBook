import json

from flask import Response


def make_succ_empty_response():
    data = json.dumps({'code': 0, 'data': {}})
    return Response(data, mimetype='application/json')


def make_succ_response(data,code=0):
    data = json.dumps({'code': code, 'data': data})
    return Response(data, mimetype='application/json')

def make_succ_page_response(data,total):
    data = json.dumps({'code': 0, 'data': data,'total':total})
    return Response(data, mimetype='application/json')


def make_err_response(err_msg):
    data = json.dumps({'code': -1, 'data': err_msg})
    return Response(data, mimetype='application/json')
