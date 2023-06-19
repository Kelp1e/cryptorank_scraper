from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, BIGINT
from sqlalchemy.orm import declarative_base, relationship

from db.setup import get_engine

Base = declarative_base()


# class Launchpad(Base):
#     __tablename__ = "launchpads"
#
#     id = Column(Integer, primary_key=True)
#     key = Column(String)
#     name = Column(String)
#     image = Column(String)
#

class SaleToken(Base):
    __tablename__ = "sale_tokens"

    id = Column(Integer, primary_key=True)

    status = Column(String)

    is_sponsored = Column(Boolean)
    name = Column(String)
    key = Column(String)
    symbol = Column(String)
    image = Column(String)

    category = Column(String)

    initial_cap = Column(BIGINT)
    raise_amount = Column(BIGINT)
    till = Column(String)
    total_raise = Column(BIGINT)

    roi = Column(Float)
    ath_roi = Column(Float)

    sale_price = Column(Float)

    # launchpads = relationship("Launchpad", backref="sale_token")


if __name__ == "__main__":
    engine = get_engine()
    Base.metadata.create_all(engine)
