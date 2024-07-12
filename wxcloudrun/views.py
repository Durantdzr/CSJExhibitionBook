from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid, \
    insert_book_record, get_book_available, delete_bookbyid
from wxcloudrun.model import Counters, Book_Record
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import requests


@app.route('/api/get_available_num', methods=['GET'])
def get_available_num():
    available = get_book_available()
    return make_succ_response(available)


@app.route('/api/book_record', methods=['POST'])
def book_record():
    """
    :return:提交预约
    """

    # 获取请求体参数
    params = request.get_json()
    record = Book_Record()

    # 检查参数
    # if 'action' not in params:
    #     return make_err_response('缺少action参数')

    record.userid = request.headers['X-WX-OPENID']
    record.book_type = params.get("book_type")
    record.book_num = params.get("book_num")
    record.booker_name = params.get("booker_name")
    record.booker_phone = params.get("booker_phone")
    record.booker_info = params.get("booker_info")
    insert_book_record(record)
    return make_succ_response(0) if record is None else make_succ_response(record.id)


@app.route('/api/get_book_history', methods=['GET'])
def get_book_history():
    """
        :return:历史预约记录列表
    """
    userid = request.headers['X-WX-OPENID']
    records = Book_Record.query.filter(Book_Record.userid == userid).all()
    result = []
    for record in records:
        result.append(
            {"id": record.id, "booker_name": record.booker_name, "book_time": record.book_time(),
             "book_mouth": record.book_mouth, "book_type": record.book_type, "book_num": record.book_num,
             'status': record.book_status()})
    return make_succ_response(result)


@app.route('/api/get_book_record', methods=['GET'])
def get_book_record():
    """
        :return:提交预约
    """
    if datetime.now() > datetime(datetime.now().year, datetime.now().month, 16):
        return make_succ_response([])
    userid = request.headers['X-WX-OPENID']
    records = Book_Record.query.filter(Book_Record.userid == userid).filter(
        Book_Record.book_mouth == datetime.now().strftime('%Y-%m')).filter(Book_Record.status == 1).all()
    result = []
    for record in records:
        result.append(
            {"id": record.id, "booker_name": record.booker_name, "book_time": record.book_time(),
             "book_mouth": record.book_mouth, "book_type": record.book_type, "book_num": record.book_num,
             'status': record.book_status()})
    return make_succ_response(result)


@app.route('/api/delete_record', methods=['POST'])
def delete_record():
    """
    :return:删除预约
    """

    # 获取请求体参数
    params = request.get_json()

    delete_bookbyid(params.get("id"))
    return make_succ_response(0)


@app.route('/api/get_user_phone', methods=['POST'])
def get_user_phone():
    """
    :return:获取手机号
    """

    # 获取请求体参数
    wxOpenid = request.headers['X-WX-OPENID']
    params = request.get_json()
    result = requests.post('http://api.weixin.qq.com/wxa/getopendata', params={"openid": wxOpenid},
                           data={'cloudid_list': [params.get("cloudid")]})

    return make_succ_response(result[0]['json']['data']['phoneNumber'])
