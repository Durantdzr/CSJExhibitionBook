from datetime import datetime

from wxcloudrun import db


class Book_Record(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'book_record'

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column('user_id', db.String(30))
    create_time = db.Column('create_time', db.TIMESTAMP, nullable=False, default=datetime.now())
    update_time = db.Column('update_time', db.TIMESTAMP, nullable=False, default=datetime.now())
    book_type = db.Column('book_type', db.String(10), nullable=False, default='上午')
    book_mouth = db.Column('book_mouth', db.String(10), nullable=False, default=datetime.now().strftime('%Y-%m'))
    booker_name = db.Column('booker_name', db.String(100))
    booker_phone = db.Column('booker_phone', db.String(100))
    booker_info = db.Column('booker_info', db.String(100))
    book_num = db.Column('book_num', db.INT, default=1)
    status = db.Column('status', db.INT, default=1)

    book_time_interval = {"上午": "09:00-11:00", "下午": "13:00-16:00"}

    def book_time(self):
        return self.book_mouth + '-28 ' + self.book_time_interval.get(self.book_type)

    def book_status(self):
        book_time=datetime.strptime(self.book_mouth, "%Y-%m")
        if self.status == 0:
            return '已取消'
        elif datetime.now() > datetime(book_time.year, book_time.month, 28):
            return '已出行'
        else:
            return '未出行'
