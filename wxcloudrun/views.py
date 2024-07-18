from datetime import datetime
from flask import request
from run import app
from wxcloudrun.dao import insert_book_record, get_book_available, delete_bookbyid, get_book_available_bytype
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
    available_num = get_book_available_bytype(params.get("book_type"))
    if int(available_num) >= int(params.get("book_num")):
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
        :return:我的预约记录列表
    """
    if datetime.now() > datetime(datetime.now().year, datetime.now().month, 28):
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
                           json={'cloudid_list': [params.get("cloudid")]})
    return make_succ_response(result.json())


@app.route('/api/get_user_book_enable', methods=['GET'])
def get_user_book_enable():
    """
        :return:获取用户预约状态
    """
    # if datetime.now() > datetime(datetime.now().year, datetime.now().month, 14, 19):
    #     return make_err_response({"status": 0, "msg": "预约时段为每月1号9:00至14号19:00，当前时段不可预约"})
    available = get_book_available()
    if available[0]["avaliable_num"] < 0 and available[1]["avaliable_num"] < 0:
        return make_err_response({"status": 0, "msg": "本月预约参观人数已满"})
    userid = request.headers['X-WX-OPENID']
    records = Book_Record.query.filter(Book_Record.userid == userid).filter(
        Book_Record.book_mouth == datetime.now().strftime('%Y-%m')).filter(Book_Record.status == 1).first()
    if records is None :
        return make_succ_response({"status": 1, "msg": "可以预约"})
    return make_err_response({"status": 0, "msg": "本月已有预约"})



@app.route('/api/send_msg', methods=['POST'])
def send_msg():
    """
        :return:发送消息
    """
    userid = request.get_json()
    wxOpenid=request.headers['X-WX-OPENID']
    data = {
        "touser": userid.get("openid"),
        "template_id": "MzOVSb0bt7cnU6zp_xOWNCDni7OrsjG5dJjVgI_teAg",
        "page": "index",
        "data": {
            "time1": {
                "value": "2019年10月1日"
            },
            "thing5": {
                "value": "长三角示范区展览馆"
            },
            "thing9": {
                "value": "您预定的参观申请因故取消，敬请谅解。"
            }
        }
    }

    result = requests.post('http://api.weixin.qq.com/cgi-bin/message/subscribe/send', params={"openid": wxOpenid},
                           json=data)

    return make_succ_response(result.json())
