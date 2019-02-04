import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class GameGenre(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="games")

    @property
    def serialize(self):
        return {
                'id': self.id,
                'name': self.name,
                'user_id': self.user_id,
        }


class ListGame(Base):
    __tablename__ = 'list_game'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    game_id = Column(Integer, ForeignKey('games.id'))
    games = relationship(GameGenre, backref=backref('list_game',
                                                    cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="list_game")

    @property
    def serialize(self):
        return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'price': self.price,
        }


engine = create_engine('sqlite:///gamelist.db')


Base.metadata.create_all(engine)
