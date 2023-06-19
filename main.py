import json
from datetime import date

from cloudscraper import create_scraper

from db.models import SaleToken
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
        sale_token = SaleToken(
            status=status,
            is_sponsored=get_value(token, "isSponsored"),
            name=get_value(token, "name"),
            key=get_value(token, "key"),
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


def main():
    upcoming_page = get_page_data(UPCOMING_API, headers, json_data)["data"]
    active_page = get_page_data(ACTIVE_API, headers, json_data)["data"]
    past_page = get_page_data(PAST_API, headers, json_data)["data"]

    load_data(upcoming_page, "upcoming")
    load_data(active_page, "active")
    load_data(past_page, "past")


if __name__ == "__main__":
    main()
