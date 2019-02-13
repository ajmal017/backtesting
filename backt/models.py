#from run import db
from sqlalchemy import create_engine, func, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
import pymysql

engine = create_engine(
      "mysql+pymysql://root:root@localhost/doom2")
#Magic123
#engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()




class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    username = Column(String(120), unique = True, nullable = False)
    password = Column(String(120), nullable = False)
    email = Column(String(120))
    firstname = Column(String(120))
    lastname = Column(String(120))
    secret = Column(String(120))
    additional = Column(String(120))
    signedup = Column(DateTime, default=func.now())
    confirmed = Column(Boolean)
    portfolios = relationship(
        "PortfolioModel",
        secondary='portfolio_usermodel_link'
    )
    dashboards = relationship(
        "DashboardModel",
        secondary='dashboard_usermodel_link'
    )
    def __init__(self, username=None, password=None, signedup=func.now(), email = None, confirmed=False):
        self.username = username
        self.password = password
        self.signedup = signedup
        self.email = email
        self.confirmed = confirmed

    def __repr__(self):
        return '<User %r>' % (self.username)
    
    def save_to_db(self):
        db_session.add(self)
        db_session.commit()
    

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username = username).first()
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email = email).first()

    def add_portfolio(self, portfolio):
        self.portfolios.append(portfolio)
        #db_session.add(self)
        #db_session.commit()
    def add_data(self):
        db_session.add(self)
    def add_commit_data(self):
        db_session.add(self)
        db_session.commit()
    def get_portfolio(self, table, portfolio):
        return db_session.query(self).filter(self.portfolios.any(table.name == portfolio)).all()[0].name
    def get_portfolios(self):
        self.query()
    def delete_portfolio(self, portfolio):       
        self.portfolios.remove(portfolio)
        db_session.add(self)
        db_session.commit()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }
        return {'users': list(map(lambda x: to_json(x), UserModel.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db_session.query(cls).delete()
            db_session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}
    
    

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)
    
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

class RevokedTokenModel(Base):
    __tablename__ = 'revoked_tokens'
    id = Column(Integer, primary_key = True)
    jti = Column(String(120))

    def __init__(self, jti=None):
        self.jti = jti

    def add(self):
        db_session.add(self)
        db_session.commit()
    
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)

class DashboardModel(Base):
    __tablename__ = 'dashboards'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    made_on = Column(DateTime, default=func.now())
    exchange = Column(String(120))
    apikey = Column(String(120))
    apisecret = Column(String(120))
    secret = Column(String(120))
    start = Column(String(16))
    end = Column(String(16))
    portfolio = Column(String(16))
    cryptocurrencies = Column(String(240))
    weights = Column(String(240))
    roi = Column(String(32))
    profit = Column(String(32))
    addition = Column(String(240))
    public = Column(Boolean)
    owner = relationship(
        UserModel,
        secondary='dashboard_usermodel_link'
    )
    def __repr__(self):
        return '<Dashboard %r>' % (self.name)

class PortfolioModel(Base):
    __tablename__ = 'portfolios'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable = False)
    made_on = Column(DateTime, default=func.now())
    owner = relationship(
        UserModel,
        secondary='portfolio_usermodel_link'
    )
    start = Column(String(16))
    end = Column(String(16))
    portfolio = Column(String(16))
    cryptocurrencies = Column(String(240))
    weights = Column(String(240))
    roi = Column(String(32))
    profit = Column(String(32))
    addition = Column(String(240))

    def __init__(self, name = None, made_on = func.now(), start = None, end = None, portfolio = None, cryptocurrencies = None, weights = None, addition = None, roi = None, profit = None ):
        self.name = name
        self.made_on = made_on
        self.start = start
        self.end = end
        self.portfolio = portfolio
        self.cryptocurrencies = cryptocurrencies
        self.weights = weights
        self.addition = addition
        self.roi = roi
        self.profit = profit
        #self.owner = owner
    
    def __repr__(self):
        return '<Portfolio %r>' % (self.name)

    def add_user(self, user):
        self.owner.append(user)
    
    def find_porfolio(cls, name):
        return cls.query.filter_by(name = name).first()
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id = id).first()
    @classmethod
    def delete_one(cls, id):
        try:
            num_rows_deleted = db_session.query(cls).filter(id = id).first().delete()
            db_session.commit()
            return {'message': '{} row deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}
    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.name,
                'owner': x.owner

            }
        return {'portfolios': list(map(lambda x: to_json(x), PortfolioModel.query.all()))}
    def get_user(self, owner):
        return db_session.query(self).filter(self.owner.any(UserModel.name == owner)).all()[0].name

    def add_data(self):
        db_session.add(self) 
    def commit(self):
        db_session.commit()

class PorfolioUserModelLink(Base):
    __tablename__ = 'portfolio_usermodel_link'
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), primary_key=True)
    usermodel_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

class DashboardUserModelLink(Base):
    __tablename__ = 'dashboard_usermodel_link'
    dashboard_id = Column(Integer, ForeignKey('dashboards.id'), primary_key=True)
    usermodel_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    #from models import User
    Base.metadata.create_all(bind=engine)

#https://www.pythoncentral.io/sqlalchemy-association-tables/