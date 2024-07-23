from datetime import datetime, timedelta
from flask import request
from run import app
from wxcloudrun.dao import insert_book_record, get_book_available, delete_bookbyid, get_book_available_bytype, \
    get_available_open_day, get_book_available_openday
from wxcloudrun.model import Book_Record, Exhibition_Open_Day
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import requests
import logging

# 初始化日志
logger = logging.getLogger('log')


@app.route('/api/get_available_num', methods=['GET'])
def get_available_num():
    openday = request.args.get('openday')
    available = get_book_available_openday(openday)
    if available is None:
        return make_err_response({"status": 0, "msg": "当前日期非可预约开放日"})
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
    record.openday = params.get("openday")
    available_num = get_book_available_bytype(params.get("book_type"), params.get("openday"))
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
    # if datetime.now() > datetime(datetime.now().year, datetime.now().month, 28):
    #     return make_succ_response([])
    userid = request.headers['X-WX-OPENID']
    records = Book_Record.query.filter(Book_Record.userid == userid, Book_Record.status == 1,
                                       Book_Record.openday >= datetime.now().strftime("%Y-%m-%d")).all()
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
    if get_book_available() < 0 :
        return make_err_response({"status": 0, "msg": "当前可预约开放日人数已满"})
    userid = request.headers['X-WX-OPENID']
    records = Book_Record.query.filter(Book_Record.userid == userid).filter(
        Book_Record.book_mouth == datetime.now().strftime('%Y-%m')).filter(Book_Record.status == 1).first()
    if records is None:
        openday = get_available_open_day()
        if len(openday) > 0:
            return make_succ_response({"status": 1, "openday": openday})
        else:
            return make_err_response({"status": 0, "msg": "当前时段无可预约开放日"})
    return make_err_response({"status": 0, "msg": "本月已有预约"})


@app.route('/api/send_msg', methods=['POST'])
def send_msg():
    """
        :return:发送消息
    """
    userid = request.get_json()
    wxOpenid = request.headers['X-WX-OPENID']
    data = {
        "touser": userid.get("openid"),
        "template_id": "MzOVSb0bt7cnU6zp_xOWNCDni7OrsjG5dJjVgI_teAg",
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
        },
        "miniprogram_state": "trial",
        "lang": "zh_CN"
    }

    result = requests.post('http://api.weixin.qq.com/cgi-bin/message/subscribe/send', params={"openid": wxOpenid},
                           json=data)

    return make_succ_response(result.json())
