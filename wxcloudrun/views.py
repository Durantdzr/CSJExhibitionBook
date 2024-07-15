from datetime import datetime
from flask import request
from run import app
from wxcloudrun.dao import insert_book_record, get_book_available, delete_bookbyid,get_book_available_bytype
from wxcloudrun.model import Book_Record
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import requests
import logging
# 初始化日志
logger = logging.getLogger('log')

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
    record.userid = request.headers['X-WX-OPENID']
    record.book_type = params.get("book_type")
    record.book_num = params.get("book_num")
    record.booker_name = params.get("booker_name")
    record.booker_phone = params.get("booker_phone")
    record.booker_info = params.get("booker_info")
    available_num=get_book_available_bytype(params.get("book_type"))
    if int(available_num)>=int(params.get("book_num")):
        insert_book_record(record)
        return make_succ_response(record.id)
    else:
        return make_err_response('超过预约人数上限')


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
    # r = result.json()

    return make_succ_response(result.json())
