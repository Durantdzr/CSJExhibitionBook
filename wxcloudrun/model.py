from datetime import datetime, timedelta

from wxcloudrun import db
import pytz

tz = pytz.timezone('Asia/Shanghai')


class Book_Record(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'book_record'

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column('user_id', db.String(30))
    create_time = db.Column('create_time', db.TIMESTAMP, nullable=False, default=datetime.now)
    update_time = db.Column('update_time', db.TIMESTAMP, nullable=False, default=datetime.now)
    book_type = db.Column('book_type', db.String(10), nullable=False, default='上午')
    book_mouth = db.Column('book_mouth', db.String(10), nullable=False)
    book_week = db.Column('book_week', db.String(10), nullable=False)
    openday = db.Column('openday', db.TIMESTAMP, nullable=False, default=datetime.now().strftime('%Y-%m-%d'))
    booker_name = db.Column('booker_name', db.String(100))
    booker_phone = db.Column('booker_phone', db.String(100))
    booker_info = db.Column('booker_info', db.String(100))
    book_num = db.Column('book_num', db.INT, default=1)
    status = db.Column('status', db.INT, default=1)

    def book_time(self):
        opentime = Exhibition_Open_Day.query.filter(Exhibition_Open_Day.openday == self.openday,
                                                    Exhibition_Open_Day.status == 1).first()
        if opentime is None:
            book_time_interval = {"上午": "09:00~11:00", "下午": "13:00~17:00"}
        else:
            book_time_interval = {"上午": str(opentime.begintime_AM) + ":00~" + str(opentime.endtime_AM) + ":00",
                                  "下午": str(opentime.begintime_PM) + ":00~" + str(opentime.endtime_PM) + ":00"}
        return self.openday.strftime('%Y-%m-%d') + " " + book_time_interval.get(self.book_type, "")

    def book_status(self):
        book_time = datetime.strptime(self.book_mouth, "%Y-%m")
        if self.status == 0:
            return '已取消'
        elif datetime.now() >= self.openday + timedelta(days=1):
            return '已出行'
        else:
            return '已预约'


class Exhibition_Open_Day(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'exhibition_open_day'

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column('userid', db.String(30))
    create_time = db.Column('create_time', db.TIMESTAMP, nullable=False, default=datetime.now)
    update_time = db.Column('update_time', db.TIMESTAMP, nullable=False, default=datetime.now)
    book_start_time = db.Column('book_start_time', db.TIMESTAMP, nullable=False)
    book_end_time = db.Column('book_end_time', db.TIMESTAMP, nullable=False)
    openday_mouth = db.Column('openday_month', db.String(10), nullable=False)
    openday = db.Column('openday', db.TIMESTAMP, nullable=False, default=datetime.now().strftime('%Y-%m-%d'))
    people_AM = db.Column('people_AM', db.INT, default=20)
    people_PM = db.Column('people_PM', db.INT, default=30)
    begintime_AM = db.Column('begintime_AM', db.INT, default=9)
    begintime_PM = db.Column('begintime_PM', db.INT, default=13)
    endtime_AM = db.Column('endtime_AM', db.INT, default=11)
    endtime_PM = db.Column('endtime_PM', db.INT, default=17)
    status = db.Column('status', db.INT, default=1)


class BlackList(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'blackList'

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column('user_id', db.String(30))
    booker_info = db.Column('booker_info', db.String(100))
    create_time = db.Column('create_time', db.TIMESTAMP, nullable=False, default=datetime.now)
    status = db.Column('status', db.INT, default=1)
class Manager(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'manager'

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column('user_id', db.String(30))