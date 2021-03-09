from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Payment(Base):
    """ Payment"""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    customer_id = Column(String(250), nullable=False)
    payment_id = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    movie = Column(String(250), nullable=False)
    movie_company = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, customer_id, payment_id, timestamp, movie, movie_company):
        """ Initializes a payment """
        self.customer_id = customer_id
        self.payment_id = payment_id
        self.timestamp = timestamp
        self.movie = movie
        self.movie_company = movie_company          
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of a payment """
        dict = {}
        dict['id'] = self.id
        dict['customer_id'] = self.customer_id
        dict['payment_id'] = self.payment_id
        dict['timestamp'] = self.timestamp
        dict['movie'] = self.movie
        dict['movie_company'] = self.movie_company
        dict['date_created'] = self.date_created

        return dict
