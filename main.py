import json
import re
import os
import time
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
    Crowdsale,
    SaleTokenCrowdsale,
)
from db.setup import create_session
from request_data import headers, json_data

scraper = create_scraper()

UPCOMING_API = "https://api.cryptorank.io/v0/round/upcoming"
ACTIVE_API = "https://api.cryptorank.io/v0/round/active"
PAST_API = "https://api.cryptorank.io/v0/round/past"


def get_date():
    current_date = date.today()
    date_string = current_date.strftime("%Y-%m-%d")

    return date_string


# JSON to Python Dict
def to_dict(string: str):
    return json.loads(string)


def get_page_data(url: str, h: dict, b: dict):
    response = scraper.post(url, headers=h, json=b)

    return to_dict(response.text)


def get_token(token_key):
    response = scraper.get(f"https://api.cryptorank.io/v0/coins/{token_key}?locale=en")

    if response.status_code == 429:
        print(f"Received 429 error. Waiting for a while... {token_key} sleep")
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


def remove_tags(string):
    if isinstance(string, str):
        formatted_string = re.sub("<[^<]+?>", "", string)

        return formatted_string

    return None


def download_image(url, key):
    os.makedirs("images", exist_ok=True)
    image_path = os.path.join("images", f"{key.lower()}.png")

    response = scraper.get(url)
    with open(image_path, "wb") as file:
        file.write(response.content)


def remove_localization_from_obj_in_array(data):
    return [{k: v for k, v in obj.items() if k != "localization"} for obj in data]


def load_sale_token(token, s):
    token_key = get_value(token, "key")

    detail_token = get_token(token_key)["data"]

    detail_token_image = get_value(get_value(detail_token, "image"), "native")
    detail_token_status = get_value(detail_token, "icoStatus")
    detail_token_has_funding_rounds = get_value(detail_token, "hasFundingRounds")
    detail_token_type = get_value(detail_token, "type")
    detail_token_life_cycle = get_value(detail_token, "lifeCycle")
    detail_token_max_supply = get_value(detail_token, "maxSupply")
    detail_token_unlimited_supply = get_value(detail_token, "unlimitedSupply")
    detail_token_total_supply = get_value(detail_token, "totalSupply")
    detail_token_is_traded = get_value(detail_token, "isTraded")
    detail_token_ico_fully_diluted_market_cap = get_value(
        detail_token, "icoFullyDilutedMarketCap"
    )
    detail_token_fully_diluted_market_cap = get_value(
        detail_token, "fullyDilutedMarketCap"
    )
    detail_token_initial_market_cap = get_value(detail_token, "initialMarketCap")
    detail_token_exist_on_tv = get_value(detail_token, "existsOnTv")
    detail_token_description = remove_tags(get_value(detail_token, "description"))
    detail_token_short_description = get_value(detail_token, "shortDescription")
    detail_token_history_start_day = get_value(detail_token, "historyStartDay")
    detail_token_history_end_day = get_value(detail_token, "historyEndDay")
    detail_token_tickers_count = get_value(detail_token, "tickersCount")
    detail_token_exchanges_count = get_value(detail_token, "exchangesCount")
    detail_token_news_count = get_value(detail_token, "newsCount")
    detail_token_watchlists_count = get_value(detail_token, "watchlistsCount")
    detail_token_has_tickers = get_value(detail_token, "hasTickers")
    detail_token_tags = [get_value(obj, "name") for obj in get_value(token, "tags")]

    # Sale Token
    sale_token_is_sponsored = get_value(token, "isSponsored")
    sale_token_name = get_value(token, "name")
    sale_token_symbol = get_value(token, "symbol")
    sale_token_category = get_value(get_value(token, "category"), "key")
    sale_token_initial_cap = get_value(token, "initialCap")
    sale_token_raise_amount = get_value(token, "raise")
    sale_token_till = get_value(token, "till")
    sale_token_total_raise = get_value(token, "totalRaise")
    sale_token_roi = get_value(token, "roi")
    sale_token_ath_roi = get_value(token, "athRoi")
    sale_token_sale_price = get_value(token, "salePrice")
    sale_token_price = get_value(token, "price")

    sale_token = s.query(SaleToken).filter_by(key=token_key).first()

    if sale_token:
        sale_token.status = detail_token_status
        sale_token.is_sponsored = sale_token_is_sponsored
        sale_token.name = sale_token_name
        sale_token.symbol = sale_token_symbol
        sale_token.category = sale_token_category
        sale_token.initial_cap = sale_token_initial_cap
        sale_token.raise_amount = sale_token_raise_amount
        sale_token.till = sale_token_till
        sale_token.total_raise = sale_token_total_raise
        sale_token.roi = sale_token_roi
        sale_token.ath_roi = sale_token_ath_roi
        sale_token.sale_price = sale_token_sale_price
        sale_token.price = sale_token_price
        sale_token.initial_market_cap = detail_token_initial_market_cap
        sale_token.has_funding_rounds = detail_token_has_funding_rounds
        sale_token.type = detail_token_type
        sale_token.life_cycle = detail_token_life_cycle
        sale_token.max_supply = detail_token_max_supply
        sale_token.unlimited_supply = detail_token_unlimited_supply
        sale_token.total_supply = detail_token_total_supply
        sale_token.is_traded = detail_token_is_traded
        sale_token.ico_fully_diluted_market_cap = (
            detail_token_ico_fully_diluted_market_cap
        )
        sale_token.fully_diluted_market_cap = detail_token_fully_diluted_market_cap
        sale_token.exist_on_tv = detail_token_exist_on_tv
        sale_token.description = detail_token_description
        sale_token.short_description = detail_token_short_description
        sale_token.history_start_day = detail_token_history_start_day
        sale_token.history_end_day = detail_token_history_end_day
        sale_token.tickers_count = detail_token_tickers_count
        sale_token.exchanges_count = detail_token_exchanges_count
        sale_token.news_count = detail_token_news_count
        sale_token.watchlists_count = detail_token_watchlists_count
        sale_token.has_tickers = detail_token_has_tickers
        sale_token.tags = detail_token_tags
    else:
        sale_token = SaleToken(
            status=detail_token_status,
            is_sponsored=sale_token_is_sponsored,
            name=sale_token_name,
            key=token_key,
            symbol=sale_token_symbol,
            category=sale_token_category,
            initial_cap=sale_token_initial_cap,
            raise_amount=sale_token_raise_amount,
            till=sale_token_till,
            total_raise=sale_token_total_raise,
            roi=sale_token_roi,
            ath_roi=sale_token_ath_roi,
            sale_price=sale_token_sale_price,
            price=sale_token_price,
            initial_market_cap=detail_token_initial_market_cap,
            has_funding_rounds=detail_token_has_funding_rounds,
            type=detail_token_type,
            life_cycle=detail_token_life_cycle,
            max_supply=detail_token_max_supply,
            unlimited_supply=detail_token_unlimited_supply,
            total_supply=detail_token_total_supply,
            is_traded=detail_token_is_traded,
            ico_fully_diluted_market_cap=detail_token_ico_fully_diluted_market_cap,
            fully_diluted_market_cap=detail_token_fully_diluted_market_cap,
            exist_on_tv=detail_token_exist_on_tv,
            description=detail_token_description,
            short_description=detail_token_short_description,
            history_start_day=detail_token_history_start_day,
            history_end_day=detail_token_history_end_day,
            tickers_count=detail_token_tickers_count,
            exchanges_count=detail_token_exchanges_count,
            news_count=detail_token_news_count,
            watchlists_count=detail_token_watchlists_count,
            has_tickers=detail_token_has_tickers,
            tags=detail_token_tags,
        )
        s.add(sale_token)
        s.commit()

    download_image(detail_token_image, token_key)

    return sale_token, detail_token


def load_launchpads(token, s, sale_token):
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
            else:
                launchpad = Launchpad(
                    key=launchpad_key,
                    name=launchpad_name,
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

            download_image(launchpad_image, launchpad_key)

            return launchpad


def load_funds(token, s, sale_token):
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
            else:
                fund = Fund(
                    key=fund_key,
                    tier=fund_tier,
                    name=fund_name,
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

            download_image(fund_image, fund_key)

            return fund


def load_blockchains(token, s, sale_token):
    blockchains_data = get_value(token, "blockchains")
    for blockchain_item in blockchains_data:
        if blockchain_item:
            blockchain_key = get_value(blockchain_item, "key")
            blockchain_name = get_value(blockchain_item, "name")
            blockchain_image = get_value(blockchain_item, "image")

            blockchain = s.query(Blockchain).filter_by(key=blockchain_key).first()
            if blockchain:
                blockchain.key = blockchain_key
                blockchain.name = blockchain_name
            else:
                blockchain = Blockchain(key=blockchain_key, name=blockchain_name)
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

            download_image(blockchain_image, blockchain_key)

            return blockchain


def load_tags(token, s, sale_token):
    pass
    # tags_data = get_value(token, "tags")
    # for tag_item in tags_data:
    #     if tag_item:
    #         tag_key = get_value(tag_item, "key")
    #         tag_name = get_value(tag_item, "name")
    #
    #         tag = s.query(Tag).filter_by(key=tag_key).first()
    #         if tag:
    #             tag.key = tag_key
    #             tag.name = tag_name
    #         else:
    #             tag = Tag(key=tag_key, name=tag_name)
    #             s.add(tag)
    #             s.commit()
    #
    #         sale_token_tag = (
    #             s.query(SaleTokenTag)
    #             .filter_by(sale_token_id=sale_token.id, tag_id=tag.id)
    #             .first()
    #         )
    #         if sale_token_tag:
    #             sale_token_tag.sale_token_id = sale_token.id
    #             sale_token_tag.tag_id = tag.id
    #         else:
    #             sale_token_tag = SaleTokenTag(
    #                 sale_token_id=sale_token.id, tag_id=tag.id
    #             )
    #             s.add(sale_token_tag)
    #             s.commit()
    #
    #         return tag


def load_crowdsales(s, sale_token, detail_token):
    crowdsales_data = get_value(detail_token, "crowdsales")
    for crowdsale_item in crowdsales_data:
        if crowdsale_item:
            crowdsale_id = get_value(crowdsale_item, "id")
            crowdsale_type = get_value(crowdsale_item, "type")
            crowdsale_start = get_value(crowdsale_item, "start")
            crowdsale_end = get_value(crowdsale_item, "end")
            crowdsale_show_only_month = get_value(crowdsale_item, "showOnlyMonth")
            crowdsale_priority_rating = get_value(crowdsale_item, "priorityRating")
            crowdsale_tokens_for_sale = get_value(crowdsale_item, "tokensForSale")
            crowdsale_lockup_period = get_value(crowdsale_item, "lockupPeriod")
            crowdsale_status = get_value(crowdsale_item, "status")
            crowdsale_is_calculate_roi_table = get_value(
                crowdsale_item, "isCalculateRoiTable"
            )
            crowdsale_is_sponsored = get_value(crowdsale_item, "isSponsored")
            crowdsale_ido_platform_key = get_value(crowdsale_item, "idoPlatformKey")
            crowdsale_price = get_value(get_value(crowdsale_item, "price"), "USD")
            crowdsale_raise_amount = get_value(
                get_value(crowdsale_item, "raise"), "USD"
            )
            crowdsale_is_closed = get_value(crowdsale_item, "isClosed")

            crowdsale = s.query(Crowdsale).filter_by(id=crowdsale_id).first()
            if crowdsale:
                crowdsale.type = crowdsale_type
                crowdsale.start = crowdsale_start
                crowdsale.end = crowdsale_end
                crowdsale.show_only_month = crowdsale_show_only_month
                crowdsale.priority_rating = crowdsale_priority_rating
                crowdsale.tokens_for_sale = crowdsale_tokens_for_sale
                crowdsale.lockup_period = crowdsale_lockup_period
                crowdsale.status = crowdsale_status
                crowdsale.is_calculate_roi_table = crowdsale_is_calculate_roi_table
                crowdsale.is_sponsored = crowdsale_is_sponsored
                crowdsale.ido_platform_key = crowdsale_ido_platform_key
                crowdsale.price = crowdsale_price
                crowdsale.raise_amount = crowdsale_raise_amount
                crowdsale.is_closed = crowdsale_is_closed
            else:
                crowdsale = Crowdsale(
                    id=crowdsale_id,
                    type=crowdsale_type,
                    start=crowdsale_start,
                    end=crowdsale_end,
                    show_only_month=crowdsale_show_only_month,
                    priority_rating=crowdsale_priority_rating,
                    tokens_for_sale=crowdsale_tokens_for_sale,
                    lockup_period=crowdsale_lockup_period,
                    status=crowdsale_status,
                    is_calculate_roi_table=crowdsale_is_calculate_roi_table,
                    is_sponsored=crowdsale_is_sponsored,
                    ido_platform_key=crowdsale_ido_platform_key,
                    price=crowdsale_price,
                    raise_amount=crowdsale_raise_amount,
                    is_closed=crowdsale_is_closed,
                )
                s.add(crowdsale)
                s.commit()

            sale_token_crowdsale = (
                s.query(SaleTokenCrowdsale)
                .filter_by(sale_token_id=sale_token.id, crowdsale_id=crowdsale.id)
                .first()
            )
            if sale_token_crowdsale:
                sale_token_crowdsale.sale_token_id = sale_token.id
                sale_token_crowdsale.crowdsale_id = crowdsale.id
            else:
                sale_token_crowdsale = SaleTokenCrowdsale(
                    sale_token_id=sale_token.id, crowdsale_id=crowdsale.id
                )
                s.add(sale_token_crowdsale)
                s.commit()

            return crowdsale


def load_data(page):
    session = create_session()
    s = session()

    for token in page:
        sale_token, detail_token = load_sale_token(token, s)
        load_launchpads(token, s, sale_token)
        load_funds(token, s, sale_token)
        load_blockchains(token, s, sale_token)
        # tag = load_tags(token, s, sale_token)
        load_crowdsales(s, sale_token, detail_token)


def main():
    upcoming_page = get_page_data(UPCOMING_API, headers, json_data)["data"]
    active_page = get_page_data(ACTIVE_API, headers, json_data)["data"]
    past_page = get_page_data(PAST_API, headers, json_data)["data"]

    load_data(upcoming_page)
    load_data(active_page)
    load_data(past_page)


if __name__ == "__main__":
    main()
