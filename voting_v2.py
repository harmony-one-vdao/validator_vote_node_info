from core.common import *
from core.smartstake_connect import find_smartstakeid

# check a single wallets vote
check_wallet = "one1prz9j6c406h6uhkyurlx9yq9h2e2zrpasr2saf"


def get_choices(eth_add, votes):
    for x in votes:
        if x["voter"] == eth_add:
            return x["choice"]


def call_snapshot_graph(args, num=100, fn=""):
    graph_params = {
        "operationName": "Votes",
        "variables": {
            "id": args[1],
            "orderBy": "vp",
            "orderDirection": "desc",
            "first": num,
            "skip": 10,
        },
        "query": """query Votes($id: String!, $first: Int, $skip: Int, $orderBy: String, $orderDirection: OrderDirection, $voter: String) {
  votes(
    first: $first
    skip: $skip
    where: {proposal: $id, vp_gt: 0, voter: $voter}
    orderBy: $orderBy
    orderDirection: $orderDirection
  ) {
    ipfs
    voter
    choice
    vp
    vp_by_strategy
  }
}""",
    }

    log.info(snapshot_graph)

    response = post(snapshot_graph, json=graph_params)
    status = response.status_code
    log.info(response)
    d = response.text
    voted = []
    if status == 200:
        try:
            d = response.json()["data"]["votes"]
            voted = [x["voter"] for x in d]
            res = True
            with open(f"{fn}.json", "w") as j:
                json.dump(d, j, indent=4)
        except json.decoder.JSONDecodeError as e:
            log.error(e)
    else:
        log.error(f"Cannot connect to API < {status} >  Error: {d[:20]}...")

    log.info(voted)
    return res, voted, d


def get_validator_voting_info(
    fn: str,
    vote_address_args: str,
    vote_name: str,
    grouped_data: dict,
    num_pages: int = 100,
    save_json_data: bool = False,
    check_wallet: bool = False,
) -> None:

    vote_address = snaphot_org_base.format(*vote_address_args)

    res, voted, voted_results = call_snapshot_graph(
        vote_address_args, fn=f"{vote_name}-{fn}"
    )

    if not res:
        log.error("Error Connecting, Shutting Down.. ")
        return False
    voted_yes_weight = 0
    voted_no_weight = 0
    voted_abstain_weight = 0
    binance_kucoin = 0
    binance_controlled_stake = 0

    csv_data = []
    result = []

    display_check = f"Wallet {check_wallet} NOT Found."

    for y in yield_data(result, check_wallet=check_wallet, num_pages=num_pages):
        result, check_wallet, show, include, v, e = y
        eth_add = convert_one_to_hex(v.address)

        if v.name in ("Binance Staking", "KuCoin"):
            binance_kucoin += e.total_delegation
            if v.name == "Binance Staking":
                binance_controlled_stake += e.total_delegation

        for d in v.delegations:
            if d["delegator-address"] == binance_wallet:
                binance_controlled_stake += d["amount"]

        if e.active_status == "active":
            w = {
                "Name": v.name,
                "Address": v.address,
                "Staked": f"{round(float(e.total_delegation) / places):,}",
                "Security Contact": v.security_contact,
                "Website": v.website,
                "Epos Status": e.epos_status,
                "Active Status": e.active_status,
            }

            grouped, app = parse_contact_info(v)

            if eth_add not in voted:
                include = True
                grouped_data[app] += grouped
                w.update({"Group": app})

            # Already Voted, Check Weight
            else:
                choices = get_choices(eth_add, voted_results)
                if not isinstance(choices, (dict, list)):
                    choices = {choices: 100}

                # for elections we just want a lst of non voters

                if isinstance(choices, list):
                    if show:
                        display_check = f"\n\tWallet *- {check_wallet} -* Voted Yes!\n"
                else:

                    for choice, percent in choices.items():
                        choice = int(choice)
                        if percent > 100 or percent in (1, 2):
                            percent = 100

                        if choice == 1:
                            voted_yes_weight += e.total_delegation // 100 * percent
                            if show:
                                display_check = (
                                    f"\n\tWallet *- {check_wallet} -* Voted Yes!\n"
                                )

                        if choice == 2:
                            voted_no_weight += e.total_delegation // 100 * percent
                            if show:
                                display_check = (
                                    f"\n\tWallet *- {check_wallet} -* Voted NO!"
                                )

                        if choice == 3:
                            voted_abstain_weight += e.total_delegation // 100 * percent
                            if show:
                                display_check = (
                                    f"\n\tWallet *- {check_wallet} -* Voted to Abstain!"
                                )

            if w["Name"] not in [x["Name"] for x in csv_data] and include:
                ss_address, ss_blskeys = find_smartstakeid(
                    v.address, smartstake_validator_list
                )
                w.update(
                    {
                        "Smartstake Summary": ss_address,
                        "Smartstake BlsKeys": ss_blskeys,
                    }
                )
                (
                    grouped_data,
                    social_media_contacts,
                ) = parse_google_docs_contact_info(v, grouped_data)

                w.update(social_media_contacts)

                csv_data.append(w)
    save_csv(
        vote_name,
        f"{vote_name}-{fn}",
        csv_data,
        [x for x in csv_data[0].keys()],
    )

    display_stats = (
        voted_abstain_weight,
        voted_no_weight,
        voted_yes_weight,
        binance_kucoin,
        binance_controlled_stake,
        display_check,
        vote_address,
    )
    save_and_display(
        vote_name,
        result,
        grouped_data,
        display_stats,
        display_vote_stats,
        save_json_data=save_json_data,
    )


if __name__ == "__main__":

    votes_to_check = {
        "RPC_DAO_Elections": (
            "harmony-mainnet.eth",
            "0x4e51760f36e580e7ae6d7f95a91ff51e5e310e9da1a0b4619cfdcb4e978a9e18",
        ),
    }

    for vote_name, vote_address_args in votes_to_check.items():
        create_folders_change_handler(vote_name)
        get_validator_voting_info(
            vote_fn,
            vote_address_args,
            vote_name,
            grouped_data,
            num_pages=100,
            save_json_data=True,
            check_wallet=check_wallet,
        )
