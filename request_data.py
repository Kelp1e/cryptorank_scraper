from fake_useragent import FakeUserAgent

user_agent = FakeUserAgent()

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
    "limit": 99999,
    "filters": {},
    "skip": 0,
    "status": "active",
}
