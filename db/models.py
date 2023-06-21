from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, BIGINT, Text
from sqlalchemy.orm import declarative_base, relationship

from db.setup import get_engine

Base = declarative_base()


class SaleToken(Base):
    __tablename__ = "sale_tokens"

    id = Column(Integer, primary_key=True)
    status = Column(String)

    # Sale Token
    is_sponsored = Column(Boolean)
    key = Column(String)
    name = Column(String)
    full_name = Column(String)
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
    price = Column(Float)

    # Detail Token
    has_funding_rounds = Column(Boolean)
    type = Column(String)
    life_cycle = Column(String)
    max_supply = Column(BIGINT)
    unlimited_supply = Column(Boolean)
    total_supply = Column(BIGINT)
    is_traded = Column(Boolean)
    ico_fully_diluted_market_cap = Column(Float)
    fully_diluted_market_cap = Column(Float)
    initial_market_cap = Column(BIGINT)
    exist_on_tv = Column(Boolean)
    description = Column(Text)
    short_description = Column(Text)
    tickers_count = Column(Integer)
    exchanges_count = Column(Integer)
    news_count = Column(Integer)
    watchlists_count = Column(Integer)
    has_tickers = Column(Boolean)

    launchpads = relationship(
        "Launchpad", secondary="sale_token_launchpad", back_populates="sale_tokens"
    )

    funds = relationship(
        "Fund", secondary="sale_token_fund", back_populates="sale_tokens"
    )

    blockchains = relationship(
        "Blockchain", secondary="sale_token_blockchain", back_populates="sale_tokens"
    )

    tags = relationship("Tag", secondary="sale_token_tag", back_populates="sale_tokens")


class Launchpad(Base):
    __tablename__ = "launchpads"

    id = Column(Integer, primary_key=True)

    key = Column(String, unique=True)
    name = Column(String)
    image = Column(String)

    sale_tokens = relationship(
        "SaleToken", secondary="sale_token_launchpad", back_populates="launchpads"
    )


class SaleTokenLaunchpad(Base):
    __tablename__ = "sale_token_launchpad"

    sale_token_id = Column(Integer, ForeignKey("sale_tokens.id"), primary_key=True)
    launchpad_id = Column(Integer, ForeignKey("launchpads.id"), primary_key=True)


class Fund(Base):
    __tablename__ = "funds"

    id = Column(Integer, primary_key=True)
    key = Column(String)
    tier = Column(Integer)
    name = Column(String)
    image = Column(String)

    sale_tokens = relationship(
        "SaleToken", secondary="sale_token_fund", back_populates="funds"
    )


class SaleTokenFund(Base):
    __tablename__ = "sale_token_fund"

    sale_token_id = Column(Integer, ForeignKey("sale_tokens.id"), primary_key=True)
    fund_id = Column(Integer, ForeignKey("funds.id"), primary_key=True)


class Blockchain(Base):
    __tablename__ = "blockchains"

    id = Column(Integer, primary_key=True)
    key = Column(String)
    name = Column(String)
    image = Column(String)

    sale_tokens = relationship(
        "SaleToken", secondary="sale_token_blockchain", back_populates="blockchains"
    )


class SaleTokenBlockchain(Base):
    __tablename__ = "sale_token_blockchain"

    sale_token_id = Column(Integer, ForeignKey("sale_tokens.id"), primary_key=True)
    blockchain_id = Column(Integer, ForeignKey("blockchains.id"), primary_key=True)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    key = Column(String)
    name = Column(String)

    sale_tokens = relationship(
        "SaleToken", secondary="sale_token_tag", back_populates="tags"
    )


class SaleTokenTag(Base):
    __tablename__ = "sale_token_tag"

    sale_token_id = Column(Integer, ForeignKey("sale_tokens.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


if __name__ == "__main__":
    engine = get_engine()
    Base.metadata.create_all(engine)
