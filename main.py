import json
from datetime import date

from cloudscraper import create_scraper

from db.models import (
    SaleToken,
    Launchpad,
    SaleTokenLaunchpad,
    Fund,
    SaleTokenFund,
    Blockchain,
    SaleTokenBlockchain,
    Tag, SaleTokenTag,
)
from db.setup import create_session
from request_data import headers, json_data

scraper = create_scraper()

UPCOMING_API = "https://api.cryptorank.io/v0/round/upcoming"
ACTIVE_API = "https://api.cryptorank.io/v0/round/active"
PAST_API = "https://api.cryptorank.io/v0/round/past"

UPCOMING_STATUS = "upcoming"
ACTIVE_STATUS = "active"
PAST_STATUS = "past"


def get_date():
    current_date = date.today()
    date_string = current_date.strftime("%Y-%m-%d")

    return date_string


def to_dict(string: str):
    return json.loads(string)


def get_page_data(url: str, h: dict, b: dict):
    response = scraper.post(url, headers=h, json=b)

    return to_dict(response.text)


def get_token_keys_from_page(page_type):
    return [token["key"] for token in page_type["data"]]


def get_token(token_key):
    response = scraper.get(f"https://api.cryptorank.io/v0/coins/{token_key}?locale=en")

    return to_dict(response.text)


def get_tokens_data_from_page(page_type):
    token_keys = get_token_keys_from_page(page_type)
    tokens_data = [get_token(token_key) for token_key in token_keys]

    return tokens_data


def get_ido_roi(group_by: str = "month", end_date: str = get_date()):
    url = (
        f"https://api.cryptorank.io/v0/analytics/ido-platforms-roi?title=ido_platforms_roi.header&"
        f"groupBy={group_by}&endDate={end_date}"
    )
    response = scraper.get(url)

    return to_dict(response.text)


def get_value(d, value):
    if isinstance(d, dict):
        return d.get(value)

    return None


def load_data(page, page_type):
    session = create_session()
    s = session()

    status = page_type

    for token in page:
        # Sale Token
        is_sponsored = get_value(token, "isSponsored")
        name = get_value(token, "name")
        token_key = get_value(token, "key")
        symbol = get_value(token, "symbol")
        image = get_value(token, "image")
        category = get_value(get_value(token, "category"), "key")
        initial_cap = get_value(token, "initialCap")
        raise_amount = get_value(token, "raise")
        till = get_value(token, "till")
        total_raise = get_value(token, "total_raise")
        roi = get_value(token, "roi")
        ath_roi = get_value(token, "athRoi")
        sale_price = get_value(token, "salePrice")
        price = get_value(token, "price")

        sale_token = s.query(SaleToken).filter_by(key=token_key).first()

        if sale_token:
            sale_token.status = status
            sale_token.is_sponsored = is_sponsored
            sale_token.name = name
            sale_token.symbol = symbol
            sale_token.image = image
            sale_token.category = category
            sale_token.initial_cap = initial_cap
            sale_token.raise_amount = raise_amount
            sale_token.till = till
            sale_token.total_raise = total_raise
            sale_token.roi = roi
            sale_token.ath_roi = ath_roi
            sale_token.sale_price = sale_price
            sale_token.price = price
        else:
            sale_token = SaleToken(
                status=status,
                is_sponsored=is_sponsored,
                name=name,
                key=token_key,
                symbol=symbol,
                image=image,
                category=category,
                initial_cap=initial_cap,
                raise_amount=raise_amount,
                till=till,
                total_raise=total_raise,
                roi=roi,
                ath_roi=ath_roi,
                sale_price=sale_price,
                price=price,
            )

            s.add(sale_token)
            s.commit()

        # Launchpads
        launchpads_data = get_value(token, "launchpads")
        for launchpads_item in launchpads_data:
            if launchpads_item:
                launchpad_key = get_value(launchpads_item, "key")
                launchpad_name = get_value(launchpads_item, "name")
                launchpad_image = get_value(launchpads_item, "image")

                launchpad = s.query(Launchpad).filter_by(key=launchpad_key).first()
                if launchpad:
                    launchpad.key = launchpad_key
                    launchpad.name = launchpad_name
                    launchpad.image = launchpad_image
                else:
                    launchpad = Launchpad(
                        key=launchpad_key,
                        name=launchpad_name,
                        image=launchpad_image,
                    )
                s.add(launchpad)
                s.commit()

                sale_token_launchpad = (
                    s.query(SaleTokenLaunchpad)
                    .filter_by(sale_token_id=sale_token.id, launchpad_id=launchpad.id)
                    .first()
                )

                if sale_token_launchpad:
                    sale_token_launchpad.sale_token_id = sale_token.id
                    sale_token_launchpad.launchpad_id = launchpad.id
                else:
                    sale_token_launchpad = SaleTokenLaunchpad(
                        sale_token_id=sale_token.id, launchpad_id=launchpad.id
                    )
                    s.add(sale_token_launchpad)
                    s.commit()

        # Funds
        funds_data = get_value(token, "funds")
        for funds_item in funds_data:
            if funds_item:
                fund_key = get_value(funds_item, "key")
                fund_tier = get_value(funds_item, "tier")
                fund_name = get_value(funds_item, "name")
                fund_image = get_value(funds_item, "image")

                fund = s.query(Fund).filter_by(key=fund_key).first()
                if fund:
                    fund.key = fund_key
                    fund.tier = fund_tier
                    fund.name = fund_name
                    fund.image = fund_image
                else:
                    fund = Fund(
                        key=fund_key, tier=fund_tier, name=fund_name, image=fund_image
                    )
                    s.add(fund)
                    s.commit()

                sale_token_fund = (
                    s.query(SaleTokenFund)
                    .filter_by(sale_token_id=sale_token.id, fund_id=fund.id)
                    .first()
                )
                if sale_token_fund:
                    sale_token_fund.sale_token_id = sale_token.id
                    sale_token_fund.fund_id = fund.id
                else:
                    sale_token_fund = SaleTokenFund(
                        sale_token_id=sale_token.id, fund_id=fund.id
                    )
                    s.add(sale_token_fund)
                    s.commit()

        # Blockchains
        blockchains_data = get_value(token, "blockchains")
        for blockchain_item in blockchains_data:
            if blockchain_item:
                blockchain_key = get_value(blockchain_item, "key")
                blockchain_name = get_value(blockchain_item, "name")
                blockchain_image = get_value(blockchain_item, "image")

                blockchain = s.query(Blockchain).filter_by(key=blockchain_key).first()
                if blockchain:
                    blockchain.name = blockchain_name
                    blockchain.image = blockchain_image
                else:
                    blockchain = Blockchain(
                        key=blockchain_key, name=blockchain_name, image=blockchain_image
                    )
                    s.add(blockchain)
                    s.commit()

                sale_token_blockchain = (
                    s.query(SaleTokenBlockchain)
                    .filter_by(sale_token_id=sale_token.id, blockchain_id=blockchain.id)
                    .first()
                )
                if sale_token_blockchain:
                    sale_token_blockchain.sale_token_id = sale_token.id
                    sale_token_blockchain.blockchain_id = blockchain.id
                else:
                    sale_token_blockchain = SaleTokenBlockchain(
                        sale_token_id=sale_token.id, blockchain_id=blockchain.id
                    )
                    s.add(sale_token_blockchain)
                    s.commit()

        # Tags
        tags_data = get_value(token, "tags")
        for tag_item in tags_data:
            if tag_item:
                tag_key = get_value(tag_item, "key")
                tag_name = get_value(tag_item, "name")

                tag = s.query(Tag).filter_by(key=tag_key).first()
                if tag:
                    tag.key = tag_key
                    tag.name = tag_name
                else:
                    tag = Tag(
                        key=tag_key,
                        name=tag_name
                    )
                    s.add(tag)
                    s.commit()

                sale_token_tag = s.query(SaleTokenTag).filter_by(
                    sale_token_id=sale_token.id,
                    tag_id=tag.id
                ).first()
                if sale_token_tag:
                    sale_token_tag.sale_token_id = sale_token.id
                    sale_token_tag.tag_id = tag.id
                else:
                    sale_token_tag = SaleTokenTag(
                        sale_token_id=sale_token.id,
                        tag_id=tag.id
                    )
                    s.add(sale_token_tag)
                    s.commit()


def main():
    upcoming_page = get_page_data(UPCOMING_API, headers, json_data)["data"]
    active_page = get_page_data(ACTIVE_API, headers, json_data)["data"]
    past_page = get_page_data(PAST_API, headers, json_data)["data"]

    load_data(upcoming_page, UPCOMING_STATUS)
    load_data(active_page, ACTIVE_STATUS)
    load_data(past_page, PAST_STATUS)


if __name__ == "__main__":
    main()
