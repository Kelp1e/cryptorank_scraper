import json
import time
from datetime import date

from cloudscraper import create_scraper
from requests import HTTPError

from db.models import (
    SaleToken,
    Launchpad,
    SaleTokenLaunchpad,
    Fund,
    SaleTokenFund,
    Blockchain,
    SaleTokenBlockchain,
    Tag,
    SaleTokenTag,
    DetailToken,
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


def get_token(token_key):
    response = scraper.get(f"https://api.cryptorank.io/v0/coins/{token_key}?locale=en")

    if response.status_code == 429:
        print(f"{token_key} sleep")
        time.sleep(10)

        response = scraper.get(
            f"https://api.cryptorank.io/v0/coins/{token_key}?locale=en"
        )

        return to_dict(response.text)

    return to_dict(response.text)


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

    for token_info in page:
        # Detail Token
        token_key = get_value(token_info, "key")

        detail_token_info = get_token(token_key)["data"]

        detail_token_name = get_value(detail_token_info, "name")
        detail_token_ico_status = get_value(detail_token_info, "icoStatus")
        detail_token_has_funding_rounds = get_value(
            detail_token_info, "hasFundingRounds"
        )
        detail_token_symbol = get_value(detail_token_info, "symbol")
        detail_token_type = get_value(detail_token_info, "type")
        detail_token_life_cycle = get_value(detail_token_info, "lifeCycle")
        detail_token_max_supply = get_value(detail_token_info, "maxSupply")
        detail_token_unlimited_supply = get_value(detail_token_info, "unlimitedSupply")
        detail_token_total_supply = get_value(detail_token_info, "totalSupply")
        detail_token_image = get_value(get_value(detail_token_info, "image"), "native")
        detail_token_category = get_value(detail_token_info, "category")
        detail_token_is_traded = get_value(detail_token_info, "isTraded")
        detail_token_ico_fully_diluted_market_cap = get_value(
            detail_token_info, "icoFullyDilutedMarketCap"
        )
        detail_token_fully_diluted_market_cap = get_value(
            detail_token_info, "fullyDilutedMarketCap"
        )

        detail_token = s.query(DetailToken).filter_by(key=token_key).first()
        if detail_token:
            detail_token.key = token_key
            detail_token.name = detail_token_name
            detail_token.ico_status = detail_token_ico_status
            detail_token.has_funding_rounds = detail_token_has_funding_rounds
            detail_token.symbol = detail_token_symbol
            detail_token.type = detail_token_type
            detail_token.life_cycle = detail_token_life_cycle
            detail_token.max_supply = detail_token_max_supply
            detail_token.unlimited_supply = detail_token_unlimited_supply
            detail_token.total_supply = detail_token_total_supply
            detail_token.image = detail_token_image
            detail_token.category = detail_token_category
            detail_token.is_traded = detail_token_is_traded
            detail_token.ico_fully_diluted_market_cap = (
                detail_token_ico_fully_diluted_market_cap
            )
            detail_token.fully_diluted_market_cap = (
                detail_token_fully_diluted_market_cap
            )
        else:
            detail_token = DetailToken(
                key=token_key,
                name=detail_token_name,
                ico_status=detail_token_ico_status,
                has_funding_rounds=detail_token_has_funding_rounds,
                symbol=detail_token_symbol,
                type=detail_token_type,
                life_cycle=detail_token_life_cycle,
                max_supply=detail_token_max_supply,
                unlimited_supply=detail_token_unlimited_supply,
                total_supply=detail_token_total_supply,
                image=detail_token_image,
                category=detail_token_category,
                is_traded=detail_token_is_traded,
                ico_fully_diluted_market_cap=detail_token_ico_fully_diluted_market_cap,
                fully_diluted_market_cap=detail_token_fully_diluted_market_cap,
            )
            s.add(detail_token)
            s.commit()

        # Sale Token
        sale_token_detail_token_id = detail_token.id
        sale_token_is_sponsored = get_value(token_info, "isSponsored")
        sale_token_name = get_value(token_info, "name")
        sale_token_symbol = get_value(token_info, "symbol")
        sale_token_image = get_value(token_info, "image")
        sale_token_category = get_value(get_value(token_info, "category"), "key")
        sale_token_initial_cap = get_value(token_info, "initialCap")
        sale_token_raise_amount = get_value(token_info, "raise")
        sale_token_till = get_value(token_info, "till")
        sale_token_total_raise = get_value(token_info, "totalRaise")
        sale_token_roi = get_value(token_info, "roi")
        sale_token_ath_roi = get_value(token_info, "athRoi")
        sale_token_sale_price = get_value(token_info, "salePrice")
        sale_token_price = get_value(token_info, "price")

        sale_token = s.query(SaleToken).filter_by(key=token_key).first()

        if sale_token:
            sale_token.detail_token_id = sale_token_detail_token_id
            sale_token.status = status
            sale_token.is_sponsored = sale_token_is_sponsored
            sale_token.name = sale_token_name
            sale_token.symbol = sale_token_symbol
            sale_token.image = sale_token_image
            sale_token.category = sale_token_category
            sale_token.initial_cap = sale_token_initial_cap
            sale_token.raise_amount = sale_token_raise_amount
            sale_token.till = sale_token_till
            sale_token.total_raise = sale_token_total_raise
            sale_token.roi = sale_token_roi
            sale_token.ath_roi = sale_token_ath_roi
            sale_token.sale_price = sale_token_sale_price
            sale_token.price = sale_token_price
        else:
            sale_token = SaleToken(
                detail_token_id=sale_token_detail_token_id,
                status=status,
                is_sponsored=sale_token_is_sponsored,
                name=sale_token_name,
                key=token_key,
                symbol=sale_token_symbol,
                image=sale_token_image,
                category=sale_token_category,
                initial_cap=sale_token_initial_cap,
                raise_amount=sale_token_raise_amount,
                till=sale_token_till,
                total_raise=sale_token_total_raise,
                roi=sale_token_roi,
                ath_roi=sale_token_ath_roi,
                sale_price=sale_token_sale_price,
                price=sale_token_price,
            )

            s.add(sale_token)
            s.commit()

        # Launchpads
        launchpads_data = get_value(token_info, "launchpads")
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
        funds_data = get_value(token_info, "funds")
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
        blockchains_data = get_value(token_info, "blockchains")
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
        tags_data = get_value(token_info, "tags")
        for tag_item in tags_data:
            if tag_item:
                tag_key = get_value(tag_item, "key")
                tag_name = get_value(tag_item, "name")

                tag = s.query(Tag).filter_by(key=tag_key).first()
                if tag:
                    tag.key = tag_key
                    tag.name = tag_name
                else:
                    tag = Tag(key=tag_key, name=tag_name)
                    s.add(tag)
                    s.commit()

                sale_token_tag = (
                    s.query(SaleTokenTag)
                    .filter_by(sale_token_id=sale_token.id, tag_id=tag.id)
                    .first()
                )
                if sale_token_tag:
                    sale_token_tag.sale_token_id = sale_token.id
                    sale_token_tag.tag_id = tag.id
                else:
                    sale_token_tag = SaleTokenTag(
                        sale_token_id=sale_token.id, tag_id=tag.id
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
