import json
from datetime import date

from cloudscraper import create_scraper

from db.models import SaleToken, Launchpad, SaleTokenLaunchpad
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


def load_pages(page, page_type):
    session = create_session()
    s = session()

    status = page_type

    for token in page:
        token_key = get_value(token, "key")
        sale_token = s.query(SaleToken).filter_by(key=token_key).first()

        if sale_token:
            sale_token.status = status
            sale_token.is_sponsored = get_value(token, "isSponsored")
            sale_token.name = get_value(token, "name")
            sale_token.symbol = get_value(token, "symbol")
            sale_token.image = get_value(token, "image")
            sale_token.category = get_value(get_value(token, "category"), "key")
            sale_token.initial_cap = get_value(token, "initialCap")
            sale_token.raise_amount = get_value(token, "raise")
            sale_token.till = get_value(token, "till")
            sale_token.total_raise = get_value(token, "totalRaise")
            sale_token.roi = get_value(token, "roi")
            sale_token.ath_roi = get_value(token, "athRoi")
            sale_token.sale_price = get_value(token, "salePrice")
        else:
            sale_token = SaleToken(
                status=status,
                is_sponsored=get_value(token, "isSponsored"),
                name=get_value(token, "name"),
                key=token_key,
                symbol=get_value(token, "symbol"),
                image=get_value(token, "image"),
                category=get_value(get_value(token, "category"), "key"),
                initial_cap=get_value(token, "initialCap"),
                raise_amount=get_value(token, "raise"),
                till=get_value(token, "till"),
                total_raise=get_value(token, "totalRaise"),
                roi=get_value(token, "roi"),
                ath_roi=get_value(token, "athRoi"),
                sale_price=get_value(token, "salePrice"),
            )

            s.add(sale_token)
            s.commit()

        launchpads_data = get_value(token, "launchpads")
        for launchpads_item in launchpads_data:
            if launchpads_item:
                launchpads_key = get_value(launchpads_item, "key")
                launchpad = s.query(Launchpad).filter_by(key=launchpads_key).first()
                if launchpad:
                    launchpad.key = launchpads_key
                    launchpad.name = get_value(launchpads_item, "name")
                    launchpad.image = get_value(launchpads_item, "image")
                else:
                    launchpad = Launchpad(
                        key=launchpads_key,
                        name=get_value(launchpads_item, "name"),
                        image=get_value(launchpads_item, "image"),
                    )
                s.add(launchpad)
                s.commit()

                sale_token_launchpad = (
                    s.query(SaleTokenLaunchpad)
                    .filter_by(sale_token_id=sale_token.id, launchpad_id=launchpad.id)
                    .first()
                )

                if not sale_token_launchpad:
                    sale_token_launchpad = SaleTokenLaunchpad(
                        sale_token_id=sale_token.id, launchpad_id=launchpad.id
                    )
                    s.add(sale_token_launchpad)
                    s.commit()


def load_data(page, page_type):
    load_pages(page, page_type)


def main():
    upcoming_page = get_page_data(UPCOMING_API, headers, json_data)["data"]
    active_page = get_page_data(ACTIVE_API, headers, json_data)["data"]
    past_page = get_page_data(PAST_API, headers, json_data)["data"]

    load_data(upcoming_page, UPCOMING_STATUS)
    load_data(active_page, ACTIVE_STATUS)
    load_data(past_page, PAST_STATUS)


if __name__ == "__main__":
    main()
