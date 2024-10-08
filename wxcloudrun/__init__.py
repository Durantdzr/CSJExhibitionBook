from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
import config
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# 因MySQLDB不支持Python3，使用pymysql扩展库代替MySQLDB库
pymysql.install_as_MySQLdb()

# 初始化web应用
app = Flask(__name__, instance_relative_config=True)
app.config['DEBUG'] = config.DEBUG

# 设定数据库链接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/exhibition_book'.format(config.username, config.password,
                                                                             config.db_address)

# 初始化DB操作对象
db = SQLAlchemy(app)
app.config['JWT_SECRET_KEY'] = 'shdata'
jwt = JWTManager(app)
CORS(app, resources={r"/api/manage/*": {"origins": '*'}},supports_credentials=True)

# 加载控制器
from wxcloudrun import views

# 加载配置
app.config.from_object('config')
