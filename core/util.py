from requests import post, Session, get
from json import dump, load
import csv
import re
from os.path import join
from collections import namedtuple
import logging

from includes.config import *

def get_all_validators(i: int, result: list) -> dict:
    d = {
        "jsonrpc": "2.0",
        "method": "hmy_getAllValidatorInformation",
        "params": [i],
        "id": 1,
    }
    data = post(harmony_api, json=d).json()["result"]
    result += data
    return result, data

def create_named_tuple_from_dict(d: dict) -> tuple:
    v = namedtuple("Validator", [d.replace("-", "_") for d in d["validator"].keys()])(
        *d["validator"].values()
    )
    e = namedtuple("Epoch", [d.replace("-", "_") for d in d.keys()])(*d.values())
    return v, e


def percentage(x: float, y: float, factor: float = 100, dp: int = 2) -> float:
    return round(((x / y) * factor), dp)

def display_vote_stats(
    voted_no_weight: int,
    voted_yes_weight: int,
    binance_kucoin: int,
    binance_controlled_stake: int,
    display_check: str,
    vote_full_address: str,
    proposal: str
) -> None:

    places = 1000000000000000000
    _, total_stake = call_api(network_info_lite)
    total_stake = round((float(total_stake["liveEpochTotalStake"]) / places))
    quorum_percentage = percentage (total_stake, 100, factor=vote_quorum)

    binance_kucoin = binance_kucoin // places
    binance_controlled_stake = binance_controlled_stake // places
    no = voted_no_weight // places
    yes = voted_yes_weight // places
    no_perc = percentage(no, total_stake)
    yes_perc = percentage(yes, total_stake)
    binance_kucoin_perc = percentage(binance_kucoin, total_stake)
    binance_control_perc = percentage(binance_controlled_stake, total_stake)

    minus_bk = int(total_stake - binance_kucoin - yes - no)

    perc_diff = vote_quorum - (yes_perc + no_perc)
    minus_bk_perc = round(100 - no_perc - yes_perc - binance_kucoin_perc, 2)

    number_left_to_pass = percentage (total_stake, 100, factor=perc_diff) 
    
    log.info(f'\nVote Proposal: {proposal}')
    log.info(f"\n\tTotal Stake         ::  {total_stake:,}\n")
    log.info(f"\tYes Vote Weight     ::  {yes:,}")
    log.info(f"\tNo Vote Weight      ::  {no:,}\n")
    log.info(f"\tVoting Stake % YES  ::  {yes_perc} %")
    log.info(f"\tVoting Stake % NO   ::  {no_perc} %\n")
    log.info(f"\t{vote_quorum} % of total       ::  {quorum_percentage:,}")
    log.info(f"\tNeeded to make 51%  ::  {number_left_to_pass:,}\n")
    log.info(f"\tBinance Kucoin      ::  {binance_kucoin:,}")
    log.info(f"\tBinance Kucoin %    ::  {binance_kucoin_perc} %")
    log.info(f"\tWeight left No B&K  ::  {minus_bk:,}")
    log.info(f"\t% left No B&K       ::  {minus_bk_perc} %\n")
    log.info(f"\tBinance Control     ::  {binance_controlled_stake:,}")
    log.info(f"\tBinance Control %   ::  {binance_control_perc} %\n")
    log.info(display_check)
    log.info(f'\tSnapshot: {vote_full_address}\n')

def display_blskey_stats(
    active_validators: int,
    is_updated: int,
    not_updated: int,
    elected: int,
    elected_is_updated: int,
    elected_not_updated: int,
    display_check: str,
    version: str
) -> None:
    # internal keys = 49%
    # external keys =51%
    # combine voting power should be more than 66.66%
    #
    # Example from Hardfork 4.3.0
    # 91% of Elected External Nodes Updated
    #TODO: calculate by number of BLSKEYS not validtors for more accurate results.
    # 49% (Internal)
    # +
    # 91% of 51% = 46.41% (External)
    #
    # = 46.41 + 49 = 95.41% (Total)
    #
    perc_not_updated = percentage(not_updated, active_validators)
    perc_updated = percentage(is_updated, active_validators)

    elec_perc_not_updated = percentage(elected_not_updated, elected)
    elec_perc_updated = percentage(elected_is_updated, elected)

    log.info(f'\nNode Version: {version}')
    log.info(f"\n\tNumber Active Validators           ::  {active_validators} ")
    log.info(f"\tHas Updated to latest version      ::  {is_updated:,}")
    log.info(f"\tNot Updated to latest version      ::  {not_updated} \n")
    log.info(f"\tHas Updated to latest version %    ::  {perc_updated} % ")
    log.info(f"\tNot Updated to latest version %    ::  {perc_not_updated} % \n")

    log.info(f"\n\tNumber Elected Validators          ::  {elected} ")
    log.info(f"\tHas Updated & Elected              ::  {elected_is_updated:,}")
    log.info(f"\tNot Updated & Elected              ::  {elected_not_updated} \n")
    log.info(f"\tHas Updated & Elected %            ::  {elec_perc_updated} % ")
    log.info(f"\tNot Updated & Elected %            ::  {elec_perc_not_updated} % \n")
    log.info(display_check)
    


def save_csv(data_folder: str, fn: str, data: list, header: list) -> None:
    with open(join("data", data_folder, fn), "w", newline="", encoding="utf-8") as csvfile:
        w = csv.writer(csvfile, delimiter=",")
        if header:
            w.writerow(header)
        for x in data:
            try:
                w.writerow(x)
            except UnicodeDecodeError:
                log.info(x)


def save_copypasta(data_folder: str, fn: str, data: list, start: str = "", end: str = "") -> None:
    data = list(set(data))
    with open(join("data", data_folder, f"{fn}.txt"), "w", encoding="utf-8") as w:
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
    log.info(response)
    d = response.text
    if response.status_code == 200:
        d = response.json()
    # log.info(d)
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
    # log.info(rtn)
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


def save_and_display(
    fn: str,
    result: dict,
    grouped_data: dict,
    display_stats: tuple,
    display: object,
    save_json_data: bool = True,
) -> None:

    for k, v in grouped_data.items():
        save_copypasta(fn, f"{fn}-" + k, v, **sep_map[k])

    if save_json_data:
        with open(all_validators_fn, "w") as j:
            dump(result, j, indent=4)

    display(*display_stats,fn)
