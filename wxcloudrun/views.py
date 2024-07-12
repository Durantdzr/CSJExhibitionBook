from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid, \
    insert_book_record, get_book_available,delete_bookbyid
from wxcloudrun.model import Counters, Book_Record
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)


@app.route('/api/user', methods=['GET'])
def insert_user():
    """
    :return: 计数的值
    """
    record = Book_Record()
    record.userid = '123'
    record.create_time = datetime.now()
    insert_book_record(record)
    return make_succ_response(0) if record is None else make_succ_response(record.id)


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

    record.userid = params.get("userid")
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
    userid = request.args.get('userid')
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
    userid = request.args.get('userid')
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
    :return:提交预约
    """

    # 获取请求体参数
    params = request.get_json()

    delete_bookbyid(params.get("id"))
    return make_succ_response(0)