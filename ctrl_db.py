from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
import psycopg2
import json

Base = declarative_base()

class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    category = Column(String)
    text = Column(String)
    ardnotify = orm.relationship("ArdNotify")
    
    def __repr__(self):
        return "<id={}, cat={}, text={}>".format(self.id, self.category, self.text)

class ArdNotify(Base):
    __tablename__ = 'ardnotify'

    id = Column(Integer, primary_key=True)
    server_id = Column(String, ForeignKey('guild.id', onupdate='CASCADE', ondelete='CASCADE'))
    news_id = Column(Integer, ForeignKey('news.id', onupdate='CASCADE', ondelete='CASCADE'))

class Guild(Base):
    __tablename__ = 'guild'

    id = Column(String, primary_key=True)
    name = Column(String)
    prefix = Column(String)
    ardnotify = orm.relationship("ArdNotify")
    dictionaly = orm.relationship("Dict")

class User(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    name = Column(String)
    speaker = Column(String)

class Dictionaly(Base):
    __tablename__ = 'dictionaly'

    id = Column(String, primary_key=True)
    word = Column(String, unique = True)
    read = Column(String)
    server_id = Column(String, ForeignKey('guild.id', onupdate='CASCADE', ondelete='CASCADE'))

url = 'postgresql+psycopg2://taro@localhost/taro_dsc'
engine = create_engine(url)

def main():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()

Session = orm.sessionmaker(bind=engine)
session = Session()

def add_news(cat, mess):
    news = News(category=cat, text=mess)

    session.add(news)
    session.commit()

def get_news():
    news = session.query(News)

    return news

def add_notify(news_id, guild_id):
    notified = ArdNotify(server_id=guild_id ,news_id=news_id)

    session.add(notified)
    session.commit()

def get_notify(guild_id):
    notifications = session.query(ArdNotify).filter_by(server_id=guild_id)

    return notifications

def add_guild(guild_id, name):
    guild = Guild(id=guild_id, name=name)

    session.add(guild)
    session.commit()

def get_guild(guild_id):
    guilds = session.query(Guild).filter_by(id=guild_id).one_or_none()

    return guilds

def add_user(user_id, name, speaker):
    user = Guild(id=guild_id, name=name, speaker=speaker)

    session.add(user)
    session.commit()

def set_user(user_id, speaker):
    user = session.query(User).filter_by(id=user_id).one()
    user.speaker = speaker

    session.commit()

def get_user(user_id):
    users = session.query(User).filter_by(id=user_id).one_or_none()

    return users