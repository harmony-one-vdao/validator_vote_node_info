from requests import post, Session, get
import json
import csv
import re
from os.path import join
from collections import namedtuple
import logging

from includes.config import *
from core.smartstake_connect import find_smartstakeid, smartstake_base
from core.google_api_connect import *

smartstake_res, smartstake_validator_list = smartstake_base()
google_contacts = download_file_from_google_drive(
    google_file_id, google_gid, google_csv_filename, save_csv=True
)


def find_weight_range(staked: int) -> str:
    if staked > 100_000_000:
        return "Above 100m"

    if staked > 20_000_000:
        return "20M - 100M"

    if staked > 5_000_000:
        return "5M - 20M"

    return "Below 5M"


def yield_data(result: list, check_wallet: bool = False, num_pages: int = 100) -> tuple:
    i = 0
    while 1:
        result, data = rpc_v2(result, "hmy_getAllValidatorInformation", [i])
        if not data or i == num_pages:
            log.info(f"NO MORE DATA.. ENDING ON PAGE {i + 1}.")
            break

        for d in data:
            show = False
            include = False

            v, e = create_named_tuple_from_dict(d)
            if v.address == check_wallet:
                show = True
            yield result, check_wallet, show, include, v, e
        i += 1


def uptime(v: namedtuple, validators: list) -> float:
    uptime_percentage = 0.00

    for x in validators["validators"]:
        if x["address"] == v.address:
            if x["uptime_percentage"]:
                uptime_percentage = round(x["uptime_percentage"] * 100, 2)
    return uptime_percentage


def time_of_block(block_number: int) -> tuple:
    _, harmony_data = rpc_v2([], "eth_getBlockByNumber", [block_number, True])
    ts = int(harmony_data["timestamp"], 16)
    date_ts = datetime.fromtimestamp(ts)
    return date_ts, date_ts.strftime("%d-%m-%y")


def months_between_dates(date_from: datetime) -> int:
    today = datetime.today()
    return (today.year - date_from.year) * 12 + today.month - date_from.month


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
        log.info(r)
        data = []
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
    voted_abstain_weight: int,
    voted_no_weight: int,
    voted_yes_weight: int,
    binance_kucoin: int,
    binance_controlled_stake: int,
    display_check: str,
    vote_full_address: str,
    proposal: str,
) -> None:

    res, _, total_stake = call_api(network_info_lite)
    if not res:
        log.error("Error Connecting, Shutting Down.. ")
        return False
    total_stake = round((float(total_stake["liveEpochTotalStake"]) / places))

    binance_kucoin = binance_kucoin // places
    binance_controlled_stake = binance_controlled_stake // places

    no = round((voted_no_weight // places), None)
    yes = round((voted_yes_weight // places), None)
    abstain = round((voted_abstain_weight // places), None)
    total_weight = round(yes + no + abstain, None)

    no_perc = percentage(no, total_stake)
    yes_perc = percentage(yes, total_stake)
    abstain_perc = percentage(abstain, total_stake)
    total_perc = round(yes_perc + no_perc + abstain_perc, 2)

    binance_kucoin_perc = percentage(binance_kucoin, total_stake)
    binance_control_perc = percentage(binance_controlled_stake, total_stake)

    minus_bk = int(total_stake - binance_kucoin - yes - no - abstain)

    perc_diff = vote_quorum - (yes_perc + no_perc + abstain_perc)
    minus_bk_perc = round(
        100 - no_perc - yes_perc - abstain_perc - binance_kucoin_perc, 2
    )

    quorum_percentage = percentage(total_stake, 100, factor=vote_quorum, dp=None)
    number_left_to_pass = percentage(total_stake, 100, factor=perc_diff, dp=None)
    perc_left_to_pass = round(vote_quorum - total_perc, 2)

    d = {
        proposal.upper(): {"Total Stake ": f"{total_stake:,}"},
        "Weights": {
            "Yes Vote Weight": f"{yes:,}",
            "No Vote Weight": f"{no:,}",
            "Abstain Vote Weight": f"{abstain:,}",
            "Total Vote Weight": f"{total_weight:,}",
        },
        "Percentages": {
            "Yes Vote %": f"{yes_perc:,} %",
            "No Vote %": f"{no_perc:,} %",
            "Abstain Vote %": f"{abstain_perc:,} %",
            "Total Vote %": f"{total_perc:,} %",
        },
        "Quorum": {
            f"{vote_quorum} % of total": f"{quorum_percentage:,}",
            "weight to make 51%": f"{number_left_to_pass:,}",
            "% to make 51%": f"{perc_left_to_pass} %",
        },
        "Binance & Kucoin": {
            "Binance & Kucoin": f"{binance_kucoin:,}",
            "Binance Kucoin %": f"{binance_kucoin_perc} %",
            "Weight left No B & K": f"{minus_bk:,}",
            "% left No B&K": f"{minus_bk_perc} %",
        },
        "Binance Controlled Stake": {
            "Binance Control": f"{binance_controlled_stake:,}",
            "Binance Control %": f"{binance_control_perc} %",
        },
        "Snapshot": {"Vote Address": vote_full_address},
    }

    # add Q% of quorum if >51%
    if total_perc > vote_quorum:
        q_no_perc = percentage(no, total_weight)
        q_yes_perc = percentage(yes, total_weight)
        q_abstain_perc = percentage(abstain, total_weight)

        d.update(
            {
                "Percentages of Quorum": {
                    "Yes Vote %": f"{q_yes_perc:,} %",
                    "No Vote %": f"{q_no_perc:,} %",
                    "Abstain Vote %": f"{q_abstain_perc:,} %",
                }
            }
        )

    csv_save_data = {}

    for title, info in d.items():
        log.info(f"\n{title}\n")
        if isinstance(info, dict):
            csv_save_data.update(info)
        for name, data in info.items():
            log.info(f"\t{name:<20}  ::  {data:<25}")

    log.info(f"\n{display_check}\n")

    save_csv(
        proposal, f"{proposal}-voting_stats.csv", [csv_save_data], csv_save_data.keys()
    )


def display_blskey_stats(
    active_validators: int,
    is_updated: int,
    not_updated: int,
    elected: int,
    elected_is_updated: int,
    elected_not_updated: int,
    display_check: str,
    version: str,
) -> None:
    # internal keys = 49%
    # external keys =51%
    # combine voting power should be more than 66.66%
    #
    # Example from Hardfork 4.3.0
    # 91% of Elected External Nodes Updated
    # TODO: calculate by number of BLSKEYS not validtors for more accurate results.
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

    log.info(f"\nNode Version: {version}")
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
    with open(
        join("data", data_folder, fn), "w", newline="", encoding="utf-8"
    ) as csvfile:
        w = csv.DictWriter(csvfile, fieldnames=header, delimiter=",")
        w.writeheader()
        for x in data:
            w.writerow(x)


def save_copypasta(
    data_folder: str, fn: str, data: list, start: str = "", end: str = ""
) -> None:
    data = list(set(data))
    with open(join("data", data_folder, f"{fn}.txt"), "w", encoding="utf-8") as w:
        for x in data:
            w.write(f"{start}{x}{end}")


def call_api(url: str, fn: str = "raw") -> tuple:

    session = Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.1.2222.33 Safari/537.36",
        "Accept-Encoding": "*",
        "Connection": "keep-alive",
    }

    res = False

    response = session.get(url)
    status = response.status_code
    log.info(response)
    d = response.text
    keys = []
    if status == 200:
        try:
            d = response.json()
            keys = [x for x in d]
            res = True
            # with open(f"{fn}.json", "w") as j:
            #     json.dump(d, j, indent=4)
        except json.decoder.JSONDecodeError as e:
            log.error(e)
    else:
        log.error(f"Cannot connect to API < {status} >  Error: {d[:20]}...")

    # log.info(d)
    return res, keys, d


def sort_group(contact: str) -> tuple:
    # Dont parse join tg chats
    if contact.startswith(("https://t.me/joinchat", "http://t.me/joinchat")):
        return [contact], "telegram"
    rtn = []
    app = "unknown"
    for k, v in expressions.items():
        lst = re.findall(v, contact)
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


def parse_google_docs_contact_info(v: namedtuple, grouped_data: dict) -> tuple:
    social_media_contacts = {}
    for x in google_contacts:
        if x["address"] == v.address:
            social_media_contacts = {con: x[con] for con in contacts_list_from_google}
            for val in social_media_contacts.values():
                if val:
                    grouped, app = sort_group(val)
                    grouped_data[app] += grouped

    return grouped_data, social_media_contacts


def open_json(fn: str) -> dict:
    with open(f"{fn}.json") as j:
        return json.load(j)


def save_and_display(
    fn: str,
    result: dict,
    grouped_data: dict,
    display_stats: tuple,
    display: object,
    save_json_data: bool = True,
) -> None:

    if grouped_data:
        for k, v in grouped_data.items():
            save_copypasta(fn, f"{fn}-" + k, v, **sep_map[k])

    if save_json_data:
        with open(all_validators_fn, "w") as j:
            json.dump(result, j, indent=4)

    if display_stats:
        display(*display_stats, fn)
