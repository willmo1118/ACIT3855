from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base
import datetime


class AddMovieOrder(Base):
    """ Add Movie Orders """

    __tablename__ = "add_movie_orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(String(250), nullable=False)
    order_id = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    movie = Column(String(250), nullable=False)
    movie_company = Column(String(250), nullable=False)
    movie_price = Column(Float, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, customer_id, order_id, timestamp, movie, movie_price, movie_company):
        """ Initializes a movie order """
        self.customer_id = customer_id
        self.order_id = order_id
        self.timestamp = timestamp
        self.movie = movie
        self.movie_price = movie_price
        self.movie_company = movie_company      
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of adding a movie order """
        dict = {}
        dict['id'] = self.id
        dict['customer_id'] = self.customer_id
        dict['order_id'] = self.order_id
        dict['timestamp'] = self.timestamp
        dict['movie'] = self.movie
        dict['movie_price'] = self.movie_price
        dict['movie_company'] = self.movie_company
        dict['date_created'] = self.date_created

        return dict
