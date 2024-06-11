# -*- coding: UTF-8 -*-
from sqlalchemy import Column,  Integer,Float,Date,  DateTime, Text, Boolean, String, ForeignKey, or_, not_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, query_expression
from sqlalchemy.sql import func
from database import Base, db_session, engine as db_engine
import datetime
from flask_login import UserMixin
from eng import manager


class Eshop(Base):
    __tablename__ = 'eshop_info'
    id = Column(Integer, primary_key=True)
    eshop_name = Column(String(100))
    eshop_phone = Column(String(12))
    eshop_email = Column(String(100))
    link_a = Column(String(100))
    link_b = Column(String(100))
    link_c = Column(String(100))

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    category_title = Column(String(100), nullable=False, default="")
    cloth = relationship("Cloth", back_populates="category")

class Cloth(Base):
    __tablename__ = 'clothes'
    id = Column(Integer, primary_key=True)
    sex = Column(Integer)
    category_type = Column(Integer, ForeignKey('categories.id'))
    category_title = Column(String(100), nullable=False)
    pic = Column(String(1000), nullable=False, default="...")
    cloth_title = Column(String(100), nullable=False, default="")
    price = Column(Integer, nullable=False, default=0)
    color = Column(String(100), nullable=False, default="")
    category = relationship('Category', back_populates='cloth')
    orders = relationship('OrderCloth', back_populates='cloth')

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_type = Column(Boolean, default=False)
    order_address = Column(String(100), nullable=False, default="")
    order_date = Column(DateTime, default=func.utcnow)
    total = Column(Integer)
    name = Column(String(100), nullable=False, default="")
    order_phone = Column(String(12), nullable=False, default="")
    clothes = relationship('OrderCloth', back_populates='order')

class OrderCloth(Base):
    __tablename__ = 'orders_clothes'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    cloth_id = Column(Integer, ForeignKey('clothes.id'))
    cloth = relationship('Cloth', back_populates='orders')
    order = relationship('Order', back_populates='clothes')
    quantity = Column(Integer, default=0)
    total = Column(Integer)

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, default="")
    surname = Column(String(100), nullable=False, default="")
    address = Column(String(100), nullable=False, default="")
    phone = Column(String(12), nullable=False, default="")
    email = Column(String(100), unique=True)
    password = Column(String(100))

class Shop(Base):
    __tablename__ = 'shops'
    id = Column(Integer, primary_key=True)
    shop_name = Column(String(100))
    shop_address = Column(String(100))
    shop_phone = Column(String(12))
    working_hour = Column(String(11))

##def example_1():
##    """
##    Добавляем группу в базу данных
##    """
##    g = Group(label = "ИСТ22-1", year=2022)
##    db_session.add(g)
##    db_session.commit()
##    print(g.id) # В этот момент у нас уже есть Id
##    # Добавляем студента
##    s = Student(
##            fio="Иванов И.И.",
##            birthday = datetime.date(1987, 4, 2),
##            sex = True,
##            group_id = g.id
##
##        )
##    db_session.add(s)
##    db_session.commit()
##    print(s.id) # Теперь у нас есть id студента
##
##
##def example_2():
##    """
##    Все тоже самое что и в 1 примере, но в одной транзакции
##    """
##    g = Group(label = "ИСТ22-1", year=2022)
##    db_session.add(g)
##    db_session.flush() # Вместо подтверждения транзакции мы вызываем данный метод
##    print(g.id) # В этот момент у нас уже есть Id
##    # Добавляем студента
##    s = Student(
##            fio="Иванов И.И.",
##            birthday = datetime.date(1987, 4, 2),
##            sex = True,
##            group_id = g.id
##
##        )
##    db_session.add(s)
##    db_session.commit()
##    print(s.id) # Теперь у нас есть id студента
##
##def example_3():
##    """
##    выборка данных
##    """
##    # Выбираем фамилии студенток и сортрируем по фио и идентификатору (последний в обратном порядке)
##    query = db_session.query(Student.fio)\
##                .filter(Student.sex == True)\
##                .order_by(Student.fio)\
##                .order_by(Student.id.desc())
##    for fio, in query.all():
##        print(fio)
##
##    # Выбираем всех студентов поступивших после 2022 года
##    query = db_session.query(Student)\
##                .join(Group)\
##                .filter(Group.year >= 2022)
##    for s in query.all():
##        print(s.fio, s.group.year)

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from database import engine
    Base.metadata.create_all(bind=engine)
    db_session.commit()

def print_schema(table_class):
    from sqlalchemy.schema import CreateTable, CreateColumn
    print(str(CreateTable(table_class.__table__).compile(db_engine)))

def print_columns(table_class, *attrNames):
   from sqlalchemy.schema import CreateTable, CreateColumn
   c = table_class.__table__.c
   print( ',\r\n'.join((str( CreateColumn(getattr(c, attrName)).compile(db_engine)) \
                            for attrName in attrNames if hasattr(c, attrName)
               )))

@manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(user_id)

if __name__ == "__main__":
    init_db()
