import logging

from sqlalchemy.exc import OperationalError

from wxcloudrun import db
from wxcloudrun.model import Book_Record

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
    available_list = {"上午": 30, '下午': 30}
    use_num = Book_Record.query.with_entities(Book_Record.book_type,
                                              db.func.sum(Book_Record.book_num).label('use_num')).group_by(
        Book_Record.book_type).all()
    for item in use_num:
        available_list[item.book_type] = int(available_list[item.book_type] - item.use_num)
    return [{"type": key, "avaliable_num": value} for key, value in available_list.items()]


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
