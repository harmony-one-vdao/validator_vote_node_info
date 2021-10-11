from core.util import *
from core.smartstake_connect import find_smartstakeid


def get_validator_voting_info(
    fn: str, num_pages: int = 10, check_vote: bool = True, save_json_data: bool = False
) -> None:
    voted, voted_results = call_api(vote_full_address)
    voted_yes_weight = 0
    voted_no_weight = 0
    binance_kucoin = 0
    binance_controlled_stake = 0

    csv_data = []
    result = []
    grouped_data = {
        "email": [],
        "twitter": [],
        "website": [],
        "telegram": [],
        "at_only": [],
        "unknown": [],
    }

    for i in range(0, num_pages):
        d = {
            "jsonrpc": "2.0",
            "method": "hmy_getAllValidatorInformation",
            "params": [i],
            "id": 1,
        }
        data = post(harmony_api, json=d).json()

        if not data["result"]:
            print(f"NO MORE DATA.. ENDING ON PAGE {i+1}.")
            break

        result += data["result"]

        for x in data["result"]:
            include = False
            v = x["validator"]
            epos_status = x["epos-status"]
            active_status = x["active-status"]

            name = v["name"]
            address = v["address"]
            contact = v["security-contact"]
            website = v["website"]
            total_delegation = x["total-delegation"]
            eth_add = convert_one_to_hex(address)

            if name in ("Binance Staking", "KuCoin"):
                binance_kucoin += total_delegation
                if name == 'Binance Staking':
                    binance_controlled_stake += total_delegation

            for d in v["delegations"]:
                if d["delegator-address"] == binance_wallet:
                    binance_controlled_stake += d["amount"]

            if check_vote:
                if eth_add not in voted:
                    include = True

            if active_status == "active":
                w = [name, address, contact, website, epos_status, active_status]
                grouped, app = sort_group(contact)
                if app == "unknown":
                    # some validators put twitter in the website column
                    # if unknown, we can try the website column,
                    # if website == unknown, we will take the unknown from the original contact..
                    grouped, app = sort_group(website)
                    if app == "unknown":
                        grouped = [contact]
                if include:
                    grouped_data[app] += grouped
                    w.append(app)
                # Already Voted, Check Weight
                else:
                    choice = voted_results[eth_add]["msg"]["payload"]["choice"]
                    if int(choice) == 1:
                        voted_yes_weight += total_delegation
                    else:
                        voted_no_weight += total_delegation

                if w[0] not in [x[0] for x in csv_data] and check_vote and include:
                    hPoolId = find_smartstakeid(address, smartstake_validator_list)
                    w += [
                        smartstake_address_summary.format(hPoolId),
                        smartstake_address_blskeys.format(hPoolId),
                    ]
                    csv_data.append(w)

    save_csv(
        f"{vote_name}-{fn}",
        csv_data, 
        [
            "Name",
            "Address",
            "Security Contact",
            "Website",
            "Epos Status",
            "Active Status",
            "Group",
            "Smartstake Summary",
            "Smartstake BlsKeys",
        ],
    )

    for k, v in grouped_data.items():
        save_copypasta(f"{vote_name}-{k}", v, **sep_map[k])

    if save_json_data:
        with open(all_validators_fn, "w") as j:
            dump(result, j, indent=4)

    display_vote_stats(voted_no_weight, voted_yes_weight, binance_kucoin, binance_controlled_stake)


if __name__ == "__main__":
    get_validator_voting_info(
        vote_fn, num_pages=10, check_vote=True, save_json_data=True
    )

    # l = call_api()
    # print(l)

    # sort_group('@ColorReader on Telegram.')
