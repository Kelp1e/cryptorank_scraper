import argparse

from fake_useragent import FakeUserAgent

user_agent = FakeUserAgent()


def get_limit():
    parser = argparse.ArgumentParser()
    parser.add_argument("--one", action="store_true")
    args = parser.parse_args()

    if args.one:
        return 50
    else:
        return 9999


headers = {
    "authority": "api.cryptorank.io",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7",
    "content-type": "application/json",
    "origin": "https://cryptorank.io",
    "referer": "https://cryptorank.io/",
    "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": user_agent.random,
}

json_data = {
    "path": "round/active",
    "limit": get_limit(),
    "filters": {},
    "skip": 0,
    "status": "active",
}
