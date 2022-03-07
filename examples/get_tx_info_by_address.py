from requests import post
from json import dump
from datetime import datetime
import logging, os, sys, csv
from collections import namedtuple
from web3 import Web3


address = "one1prz9j6c406h6uhkyurlx9yq9h2e2zrpasr2saf"
harmony_api = "https://a.api.s0.t.hmny.io"  # Archive node


def create_data_path(pth: str, data_path: str = "data") -> os.path:
    cwd = os.getcwd()
    p = os.path.join(cwd, data_path, pth)
    if not os.path.exists(p):
        os.mkdir(p)
    return p


def create_named_tuple_from_dict(d: dict) -> tuple:
    v = namedtuple("Validator", [d.replace("-", "_") for d in d["validator"].keys()])(
        *d["validator"].values()
    )
    e = namedtuple("Epoch", [d.replace("-", "_") for d in d.keys()])(*d.values())
    return v, e


def yield_data(address: str, num_pages: int = 10) -> tuple:
    i = 0
    result = []
    while 1:
        params = [
            {
                "address": address,
                "pageIndex": i,
                "fullTx": True,
                "txType": "ALL",
                "order": "DESC",
            }
        ]
        result, data = rpc_v2(result, "hmyv2_getTransactionsHistory", params)
        if not data or i == num_pages:
            log.info(f"NO MORE DATA.. ENDING ON PAGE {i + 1}.")
            break
        i += 1

    with open(os.path.join("data", "tx_data.json"), "w") as j:
        dump(result, j, indent=4)
    return result


def rpc_v2(
    result: list,
    method: str,
    params: list,
) -> dict:

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
    result += data["transactions"]
    return result, data


def save_csv(fn: str, data: list) -> None:
    data = convert_unix_time_and_one(data)
    header = data[0].keys()
    with open(os.path.join("data", fn), "w", newline="", encoding="utf-8") as csvfile:
        w = csv.DictWriter(csvfile, fieldnames=header, delimiter=",")
        w.writeheader()
        for x in data:
            w.writerow(x)


def convert_unix_time_and_one(data: list) -> list:
    fmt = "%Y-%m-%d %H:%M:%S"
    rtn = []
    for x in data:
        new_d = x
        new_d.update(
            {
                "timestamp": datetime.fromtimestamp(x["timestamp"]).strftime(fmt),
                "value": Web3.fromWei(x["value"], "ether"),
            }
        )
        rtn.append(new_d)
    return rtn


if __name__ == "__main__":
    create_data_path((""))

    file_handler = logging.FileHandler(filename=os.path.join("data", "data.log"))
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=handlers)

    log = logging.getLogger()

    data = yield_data(address, num_pages=2)
    save_csv("Tx_Date.csv", data)
