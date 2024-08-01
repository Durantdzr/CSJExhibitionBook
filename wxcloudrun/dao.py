import logging

from sqlalchemy.exc import OperationalError

from wxcloudrun import db
from wxcloudrun.model import Book_Record, Exhibition_Open_Day,BlackList
from datetime import datetime, timedelta
import requests
# 初始化日志
logger = logging.getLogger('log')


def insert_book_record(book_record):
    """
    插入一个Book_Record实体
    :param counter: Counters实体
    """
    try:
        db.session.add(book_record)
        db.session.commit()
    except OperationalError as e:
        logger.info("insert_counter errorMsg= {} ".format(e))


def get_book_available():
    available_num = 0
    use_num = 0
    opendays = Exhibition_Open_Day.query.filter(Exhibition_Open_Day.status == 1,
                                                Exhibition_Open_Day.book_start_time <= datetime.now(),
                                                Exhibition_Open_Day.book_end_time >= datetime.now()).all()
    for openday in opendays:
        available_num += openday.people_AM
        available_num += openday.people_PM

        record = Book_Record.query.with_entities(db.func.sum(Book_Record.book_num).label('use_num')).filter(
            Book_Record.status == 1, Book_Record.openday == openday.openday).first()
        if record[0] is not None:
            use_num+=record.use_num
    return available_num-use_num


def get_book_available_openday(openday=datetime.now().strftime('%Y-%m-%d')):
    openday_available = Exhibition_Open_Day.query.filter(Exhibition_Open_Day.openday == openday,
                                                         Exhibition_Open_Day.status == 1).first()
    if openday_available is None:
        return None
    available_list = {"上午": openday_available.people_AM, '下午': openday_available.people_PM}
    interval={"上午": str(openday_available.begintime_AM) + ":00-" + str(openday_available.endtime_AM) + ":00",
                                  "下午": str(openday_available.begintime_PM) + ":00-" + str(openday_available.endtime_PM) + ":00"}
    use_num = Book_Record.query.with_entities(Book_Record.book_type,
                                              db.func.sum(Book_Record.book_num).label('use_num')).filter(
        Book_Record.status == 1, Book_Record.openday == openday).group_by(
        Book_Record.book_type).all()
    for item in use_num:
        available_list[item.book_type] = int(available_list[item.book_type] - item.use_num)
    return [{"type": key, "avaliable_num": value,"interval":interval.get(key)} for key, value in available_list.items()]


def get_book_available_bytype(book_type, openday):
    openday_available = Exhibition_Open_Day.query.filter(Exhibition_Open_Day.openday == openday,
                                                         Exhibition_Open_Day.status == 1).first()
    if book_type == '上午':
        available_num = openday_available.people_AM
    else:
        available_num = openday_available.people_PM
    use_num = Book_Record.query.with_entities(db.func.sum(Book_Record.book_num).label('use_num')).filter(
        Book_Record.status == 1, Book_Record.book_type == book_type, Book_Record.openday == openday).first()
    if use_num[0] is None:
        return available_num
    else:
        return available_num - use_num[0]


def delete_bookbyid(id):
    """
    根据ID查询Counter实体
    :param id: Counter的ID
    :return: Counter实体
    """
    try:
        record = Book_Record.query.filter(Book_Record.id == id).first()
        record.status = 0
        db.session.commit()
    except OperationalError as e:
        logger.info("query_counterbyid errorMsg= {} ".format(e))
        return None


def get_available_open_day():
    opendays = Exhibition_Open_Day.query.filter(Exhibition_Open_Day.status == 1,
                                                Exhibition_Open_Day.book_start_time <= datetime.now(),
                                                Exhibition_Open_Day.book_end_time >= datetime.now()).all()
    return [item.openday.strftime('%Y-%m-%d') for item in opendays]


def insert_black_list(blacklist):
    """
    插入一个Book_Record实体
    :param counter: Counters实体
    """
    try:
        db.session.add(blacklist)
        db.session.commit()
    except OperationalError as e:
        logger.info("insert_counter errorMsg= {} ".format(e))

def delete_blacklistbyinfo(booker_info):
    """
    :param id: Counter的ID
    :return: Counter实体
    """
    try:
        record = BlackList.query.filter(BlackList.booker_info == booker_info,BlackList.status==1).first()
        record.status = 0
        db.session.commit()
    except OperationalError as e:
        logger.info("query_counterbyid errorMsg= {} ".format(e))
        return None

def insert_openday(openday):
    """
    插入一个Book_Record实体
    :param counter: Counters实体
    """
    try:
        db.session.add(openday)
        db.session.commit()
    except OperationalError as e:
        logger.info("insert_counter errorMsg= {} ".format(e))

def update_opendaybyday(openday,dict):
    """
    根据ID查询Counter实体
    :param id: Counter的ID
    :return: Counter实体
    """
    try:
        openday = Exhibition_Open_Day.query.filter(Exhibition_Open_Day.openday == openday,Exhibition_Open_Day.status==1).first()
        openday.people_AM = dict['people_AM']
        openday.people_PM = dict['people_PM']
        openday.begintime_AM = dict['begintime_AM']
        openday.begintime_PM = dict['begintime_PM']
        openday.endtime_AM = dict['endtime_AM']
        openday.endtime_PM = dict['endtime_PM']
        db.session.commit()
        return openday.id
    except OperationalError as e:
        logger.info("query_counterbyid errorMsg= {} ".format(e))
        return None
def delete_opendaybyday(openday):
    """
    :param id: Counter的ID
    :return: Counter实体
    """
    try:
        record = Exhibition_Open_Day.query.filter(Exhibition_Open_Day.openday == openday,Exhibition_Open_Day.status==1).first()
        record.status = 0
        db.session.commit()
        records=Book_Record.query.filter(Book_Record.openday==openday,Book_Record.status==1).all()
        for record in records:
            record.status=0
            send_cancel_msg(record.user_id,record.openday.strftime('%Y年%m月%d日'))
        db.session.commit()
    except OperationalError as e:
        logger.info("query_counterbyid errorMsg= {} ".format(e))
        return None

def send_cancel_msg(openid,openday):
    data = {
        "touser": openid,
        "template_id": "MzOVSb0bt7cnU6zp_xOWNCDni7OrsjG5dJjVgI_teAg",
        "data": {
            "time1": {
                "value": openday
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

    result = requests.post('http://api.weixin.qq.com/cgi-bin/message/subscribe/send', params={"openid": openid},
                           json=data)