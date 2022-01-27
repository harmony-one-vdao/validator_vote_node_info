from requests import get, post
from json import dump
from datetime import datetime

block_number = 10000000
harmony_api = "https://api.harmony.one"


def rpc_v2(result: list, method: str, params: list) -> dict:
    d = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }
    try:
        r = post(harmony_api, json=d)
        data = r.json()["result"]
    except KeyError:
        print(r)
        data = r.json()
    result += data
    return result, data


def time_of_block(block_number: int) -> str:
    res, harmony_data = rpc_v2([], "eth_getBlockByNumber", [block_number, True])
    ts = int(harmony_data["timestamp"], 16)
    date_ts = datetime.fromtimestamp(ts)
    return date_ts, date_ts.strftime("%d-%m-%y")


def months_between_dates(date_from: datetime) -> int:
    today = datetime.today()
    return (today.year - date_from.year) * 12 + today.month - date_from.month


created_dt, created_str = time_of_block(18867042)
print(created_str)
months = months_between_dates(created_dt)
print(months)

address = "one1prz9j6c406h6uhkyurlx9yq9h2e2zrpasr2saf"
# address = "one1dsj3lknm2caqpff74j9tade6wlc4vmyt4hxfcv"
res, data = rpc_v2([], "hmyv2_getValidatorInformation", [address])
print(data)
