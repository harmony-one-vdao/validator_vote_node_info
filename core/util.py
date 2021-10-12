from requests import post, Session, get
from json import dump, load
import csv
import re
from os.path import join
from collections import namedtuple

from includes.config import *


def create_named_tuple_from_dict(d: dict) -> tuple:
    v = namedtuple('Validator', [d.replace('-', '_') for d in d['validator'].keys()])(*d['validator'].values())
    e = namedtuple('Epoch', [d.replace('-', '_') for d in d.keys()])(*d.values())
    return v, e

def display_vote_stats(
    voted_no_weight: int, voted_yes_weight: int, binance_kucoin: int, binance_controlled_stake: int, display_check: str
) -> None:

    places = 1000000000000000000
    _, total_stake = call_api(network_info_lite)
    total_stake = round((float(total_stake["liveEpochTotalStake"]) / places))
    number_51 = round((total_stake / 100) * 51)

    binance_kucoin = binance_kucoin // places
    binance_controlled_stake = binance_controlled_stake // places
    no = voted_no_weight // places
    yes = voted_yes_weight // places
    no_perc = round(((no / total_stake) * 100), 2)
    yes_perc = round(((yes / total_stake) * 100), 2)
    binance_kucoin_perc = round(((binance_kucoin / total_stake) * 100), 2)
    binance_control_perc = round(((binance_controlled_stake / total_stake) * 100), 2)

    minus_bk = int(total_stake - binance_kucoin - yes - no)

    perc_diff = 51 - (yes_perc + no_perc)
    minus_bk_perc = round(100 - no_perc - yes_perc - binance_kucoin_perc, 2)

    number_left_to_pass = round((total_stake / 100) * perc_diff)

    print(f"\nTotal Stake         ::  {total_stake:,}")
    print(f"Yes Vote Weight     ::  {yes:,}")
    print(f"No Vote Weight      ::  {no:,}")
    print(f"Voting Stake % YES  ::  {yes_perc} %")
    print(f"Voting Stake % NO   ::  {no_perc} %")
    print(f"51 % of total       ::  {number_51:,}")
    print(f"Needed to make 51%  ::  {number_left_to_pass:,}")
    print(f"Binance Kucoin      ::  {binance_kucoin:,}")
    print(f"Binance Kucoin %    ::  {binance_kucoin_perc} %")
    print(f"Weight left No B&K  ::  {minus_bk:,}")
    print(f"% left No B&K       ::  {minus_bk_perc} %\n")
    print(f"Binance Control     ::  {binance_controlled_stake:,}")
    print(f"Binance Control %   ::  {binance_control_perc} %\n")
    print(display_check)


def display_blskey_stats(
    active_validators: int, is_updated: int, not_updated: int, elected: int, elected_is_updated: int, elected_not_updated: int, display_check: str
) -> None:
    perc_not_updated = round((not_updated / active_validators ) * 100, 2 )
    perc_updated = round((is_updated / active_validators) * 100, 2)

    elec_perc_not_updated = round((elected_not_updated / elected ) * 100, 2 )
    elec_perc_updated = round((elected_is_updated / elected) * 100, 2)

    print(f"\n\tNumber Active Validators           ::  {active_validators} ")
    print(f"\tHas Updated to latest version      ::  {is_updated:,}")
    print(f"\tNot Updated to latest version      ::  {not_updated} \n")
    print(f"\tHas Updated to latest version %    ::  {perc_updated} % ")
    print(f"\tNot Updated to latest version %    ::  {perc_not_updated} % \n")

    print(f"\n\tNumber Elected Validators          ::  {elected} ")
    print(f"\tHas Updated & Elected              ::  {elected_is_updated:,}")
    print(f"\tNot Updated & Elected              ::  {elected_not_updated} \n")
    print(f"\tHas Updated & Elected %            ::  {elec_perc_updated} % ")
    print(f"\tNot Updated & Elected %            ::  {elec_perc_not_updated} % \n")
    print(display_check)

def save_csv(fn: str, data: list, header: list) -> None:
    with open(join("data", fn), "w", newline="", encoding="utf-8") as csvfile:
        w = csv.writer(csvfile, delimiter=",")
        if header:
            w.writerow(header)
        for x in data:
            try:
                w.writerow(x)
            except UnicodeDecodeError:
                print(x)


def save_copypasta(fn: str, data: list, start: str = "", end: str = "") -> None:
    data = list(set(data))
    with open(join("data", f"{fn}.txt"), "w", encoding="utf-8") as w:
        for x in data:
            w.write(f"{start}{x}{end}")


def call_api(url: str) -> tuple:

    session = Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.1.2222.33 Safari/537.36",
        "Accept-Encoding": "*",
        "Connection": "keep-alive",
    }

    response = session.get(url)
    print(response)
    d = response.text
    if response.status_code == 200:
        d = response.json()
    # print(d)
    return [x for x in d], d

def sort_group(contact: str) -> tuple:
    rtn = []
    app = "unknown"
    for k, v in expressions.items():
        lst = re.findall(v, contact.lower())
        if lst:
            rtn = lst
            app = k
            break
    if app == "at_only":
        rtn = [f"@{x.split('@')[-1]}" for x in rtn]
    for x in rtn:
        if x in blacklist:
            rtn = []
            break
    # print(rtn)
    return rtn, app

def parse_contact_info(v: namedtuple) -> tuple:
    grouped, app = sort_group(v.security_contact)
    if app == "unknown":
        # some validators put twitter in the website column
        # if unknown, we can try the website column,
        # if website == unknown, we will take the unknown from the original v.security_contact..
        grouped, app = sort_group(v.website)
        if app == "unknown":
            grouped = [v.security_contact]
    return grouped, app


def open_json(fn: str) -> dict:
    with open(f"{fn}.json") as j:
        return load(j)

def save_and_display(fn: str, result: dict, grouped_data: dict, display_stats: tuple, display: object, save_json_data: bool = True) -> None:

    for k, v in grouped_data.items():
        save_copypasta(fn + k, v, **sep_map[k])

    if save_json_data:
        with open(all_validators_fn, "w") as j:
            dump(result, j, indent=4)

    display(*display_stats)
