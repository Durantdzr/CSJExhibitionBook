from datetime import datetime, timedelta
from flask import request
from run import app
from wxcloudrun.dao import insert_book_record, get_book_available, delete_bookbyid, get_book_available_bytype, \
    get_available_open_day, get_book_available_openday, insert_black_list, delete_blacklistbyinfo, insert_openday, \
    update_opendaybyday, delete_opendaybyday
from wxcloudrun.model import Book_Record, Exhibition_Open_Day, BlackList,Manager
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response, make_succ_page_response
import requests
import logging
import pytz
from dateutil.relativedelta import relativedelta
from wxcloudrun import db
from sqlalchemy import or_, and_

tz = pytz.timezone('Asia/Shanghai')
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
    black = BlackList.query.filter(BlackList.status == 1, BlackList.booker_info == params.get("booker_info")).first()
    if black is not None:
        return make_err_response('该用户不可预约')
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
    records = Book_Record.query.filter(or_(and_(Book_Record.userid == userid, Book_Record.status == 0),
                                           and_(Book_Record.userid == userid,
                                                Book_Record.openday == datetime.now().strftime('%Y-%m-%d')))).all()
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
    userid = request.headers['X-WX-OPENID']
    records = Book_Record.query.filter(Book_Record.userid == userid, Book_Record.status == 1,
                                       Book_Record.openday >= datetime.now(tz=tz).strftime("%Y-%m-%d")).all()
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
    if get_book_available() < 0:
        return make_err_response({"status": 0, "msg": "当前可预约开放日人数已满"})
    userid = request.headers['X-WX-OPENID']
    records = Book_Record.query.filter(Book_Record.userid == userid, Book_Record.status == 1,
                                       Book_Record.openday >= datetime.now().strftime("%Y-%m-%d")).first()
    # records = None
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
        "template_id": "YD4H4lqbmqQ2KsnpXQT-rJqfdEkC0CKgQzSXyn3rDrc",
        "data": {
            "thing1": {
                "value": "长三角示范区展览馆"
            },
            "time2": {
                "value": "2020年4月15日"
            },
            "time3": {
                "value": "08:00-10:00"
            },
            "thing4": {
                "value": "您的预约因故自动更换参观时段，敬请谅解"
            }
        },
        "miniprogram_state": "trial",
        "lang": "zh_CN"
    }

    result = requests.post('http://api.weixin.qq.com/cgi-bin/message/subscribe/send', params={"openid": wxOpenid},
                           json=data)

    return make_succ_response(result.json())


@app.route('/api/manage/get_total_book_record', methods=['GET'])
def get_total_book_record():
    """
        :return:获取预约信息数据
    """
    wxOpenid = request.headers['X-WX-OPENID']
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)
    booker_name = request.args.get('booker_name', default=None)
    openday = request.args.get('openday', default=None)
    if booker_name is None and openday is None:
        records = Book_Record.query.order_by(Book_Record.openday.desc(), Book_Record.book_type.asc(),
                                             Book_Record.booker_name.desc(),
                                             Book_Record.booker_phone.desc()).paginate(page, per_page=page_size,
                                                                                       error_out=False)
    else:
        filters = []
        if booker_name is not None:
            filters.append(Book_Record.booker_name == booker_name)
        if openday is not None:
            filters.append(Book_Record.openday == openday)
        records = Book_Record.query.filter(*filters).order_by(
            Book_Record.openday.desc(),
            Book_Record.book_type.asc(),
            Book_Record.booker_name.desc(),
            Book_Record.booker_phone.desc(),
        ).paginate(page,
                   per_page=page_size,
                   error_out=False)
    return make_succ_page_response(
        data=[{"id": record.id, "booker_name": record.booker_name, "book_num": record.book_num,
               "book_type": record.book_type, "booker_phone": record.booker_phone,
               "book_time": record.book_time(), 'status': record.book_status()} for record in
              records.items], total=records.total)


@app.route('/api/manage/create_blacklist', methods=['POST'])
def create_blacklist():
    """
        :return:创建黑名单
    """
    # 获取请求体参数
    params = request.get_json()
    result = BlackList.query.filter(BlackList.booker_info == params['booker_info'], BlackList.status == 1).first()
    if result is not None:
        return make_err_response('该用户已在黑名单中')
    blacklist = BlackList()
    blacklist.userid = request.headers['X-WX-OPENID']
    blacklist.booker_info = params['booker_info']
    insert_black_list(blacklist)
    return make_succ_response(blacklist.id)


@app.route('/api/manage/delete_blacklist', methods=['POST'])
def delete_blacklist():
    """
        :return:删除黑名单
    """
    # 获取请求体参数
    wxOpenid = request.headers['X-WX-OPENID']
    params = request.get_json()
    delete_blacklistbyinfo(params['booker_info'])
    return make_succ_response(0)


@app.route('/api/manage/get_blacklist', methods=['GET'])
def get_blacklist():
    wxOpenid = request.headers['X-WX-OPENID']
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)
    booker_info = request.args.get('booker_info', default='')
    lists = BlackList.query.filter(BlackList.status == 1, BlackList.booker_info.like('%' + booker_info + '%')).order_by(
        BlackList.create_time.desc()).paginate(page,
                                               per_page=page_size,
                                               error_out=False)
    return make_succ_response(
        [{"booker_info": record.booker_info, "create_time": record.create_time.strftime('%Y年%m月%d日 %H:%M:%S')} for
         record in
         lists.items])


@app.route('/api/manage/create_openday', methods=['POST'])
def create_openday():
    """
        :return:创建预约开放日
    """
    # 获取请求体参数
    params = request.get_json()
    openday = Exhibition_Open_Day()
    openday.userid = request.headers['X-WX-OPENID']
    openday.openday = datetime.strptime(params['openday'], "%Y-%m-%d")
    openday.people_AM = params['people_AM']
    openday.people_PM = params['people_PM']
    openday.begintime_AM = params['begintime_AM']
    openday.begintime_PM = params['begintime_PM']
    openday.endtime_AM = params['endtime_AM']
    openday.endtime_PM = params['endtime_PM']
    insert_openday(openday)
    return make_succ_response(openday.id)


@app.route('/api/manage/update_openday', methods=['POST'])
def update_openday():
    """
        :return:创建预约开放日
    """
    # 获取请求体参数
    params = request.get_json()
    id = update_opendaybyday(datetime.strptime(params['openday'], "%Y-%m-%d"), params)

    return make_succ_response(id)


@app.route('/api/manage/delete_openday', methods=['POST'])
def delete_openday():
    """
        :return:删除预约开放日
    """
    # 获取请求体参数
    params = request.get_json()
    delete_opendaybyday(datetime.strptime(params['openday'], "%Y-%m-%d"))
    return make_succ_response(0)


@app.route('/api/manage/get_openday_bymonth', methods=['GET'])
def get_openday_bymonth():
    """
        :return:按月份预约日查询
    """
    # 获取请求体参数
    openday_month = request.args.get('month', default=datetime.now(tz=tz).strftime('%Y-%m'))
    list = Exhibition_Open_Day.query.filter(Exhibition_Open_Day.status == 1,
                                            Exhibition_Open_Day.openday_mouth == openday_month).all()
    return make_succ_response([item.openday.strftime('%Y-%m-%d') for item in list])

@app.route('/api/manage/privilege', methods=['GET'])
def get_manager_privilege():
    """
        :return:按月份预约日查询
    """
    # 获取请求体参数
    userid = request.headers['X-WX-OPENID']
    result=Manager.query.filter(Manager.userid ==userid).first()
    if result is not None:
        return make_succ_response(True)
    else:
        return make_succ_response(False)

@app.route('/api/manage/get_openday_byday', methods=['GET'])
def get_openday_byday():
    """
        :return:按预约日查询已编辑信息
    """
    # 获取请求体参数
    openday = request.args.get('openday', default=datetime.now(tz=tz).strftime('%Y-%m-%d'))
    info = Exhibition_Open_Day.query.filter(Exhibition_Open_Day.status == 1,
                                            Exhibition_Open_Day.openday == openday).first()
    if info is None:
        return make_err_response(
            {"people_AM": 20, "people_PM": 30, "begintime_AM": 9, "begintime_PM": 13, "endtime_AM": 11,
             "endtime_PM": 17})
    return make_succ_response(
        {"people_AM": info.people_AM, "people_PM": info.people_PM, "begintime_AM": info.begintime_AM,
         "begintime_PM": info.begintime_PM, "endtime_AM": info.endtime_AM, "endtime_PM": info.endtime_PM})


@app.route('/api/manage/get_book_statistics', methods=['GET'])
def get_book_statistics():
    """
        :return:预约信息统计
    """
    # 获取请求体参数
    begintime = request.args.get('begintime', default=datetime.now(tz=tz).strftime('%Y-%m-%d'))
    type = request.args.get('type', default='month')
    interval = request.args.get('interval', default=5, type=int)
    data = []
    if type == 'month':
        result = Book_Record.query.with_entities(Book_Record.book_type, Book_Record.book_mouth,
                                                 db.func.sum(Book_Record.book_num).label('use_num')).filter(
            Book_Record.status == 1,
            Book_Record.book_mouth <= datetime.strptime(begintime, '%Y-%m-%d').strftime('%Y-%m'),
            Book_Record.book_mouth >= (
                    datetime.strptime(begintime, '%Y-%m-%d') - relativedelta(months=interval)).strftime(
                '%Y-%m')).group_by(Book_Record.book_type, Book_Record.book_mouth).all()
        for month_interval in range(interval, -1, -1):
            month_data = {'name': '近' + str(month_interval) + '月' if month_interval > 0 else '本月', "上午": 0,
                          "下午": 0}
            for item in result:
                if item[1] == (
                        datetime.strptime(begintime, '%Y-%m-%d') - relativedelta(months=month_interval)).strftime(
                    '%Y-%m'):
                    month_data[item[0]] += int(item[2])
            data.append(month_data)
    if type == 'day':
        result = Book_Record.query.with_entities(Book_Record.book_type, Book_Record.openday,
                                                 db.func.sum(Book_Record.book_num).label('use_num')).filter(
            Book_Record.status == 1, Book_Record.openday <= datetime.strptime(begintime, '%Y-%m-%d'),
            Book_Record.openday >= datetime.strptime(begintime, '%Y-%m-%d') - timedelta(days=interval)).group_by(
            Book_Record.book_type, Book_Record.openday).all()
        for day_interval in range(interval, -1, -1):
            day_data = {'name': '近' + str(day_interval) + '天' if day_interval > 0 else '本日', "上午": 0,
                        "下午": 0}
            for item in result:
                if item[1] == datetime.strptime(begintime, '%Y-%m-%d') - timedelta(days=day_interval):
                    day_data[item[0]] += int(item[2])
            data.append(day_data)
    if type == 'week':
        result = Book_Record.query.with_entities(Book_Record.book_type, Book_Record.book_week,
                                                 db.func.sum(Book_Record.book_num).label('use_num')).filter(
            Book_Record.status == 1,
            Book_Record.book_week <= datetime.strptime(begintime, '%Y-%m-%d').strftime('%Y-%U'),
            Book_Record.book_week >= (
                    datetime.strptime(begintime, '%Y-%m-%d') - relativedelta(weeks=interval)).strftime(
                '%Y-%U')).group_by(Book_Record.book_type, Book_Record.book_week).all()
        for week_interval in range(interval, -1, -1):
            month_data = {'name': '近' + str(week_interval) + '周' if week_interval > 0 else '本周', "上午": 0,
                          "下午": 0}
            for item in result:
                if item[1] == (
                        datetime.strptime(begintime, '%Y-%m-%d') - relativedelta(weeks=week_interval)).strftime(
                    '%Y-%U'):
                    month_data[item[0]] += int(item[2])
            data.append(month_data)
    for item in data:
        item['AM'] = item['上午']
        item['PM'] = item['下午']
        del item['上午']
        del item['下午']
    return make_succ_response(data)
