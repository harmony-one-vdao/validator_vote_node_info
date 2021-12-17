from core.common import *
from core.smartstake_connect import find_smartstakeid

# check a single wallets vote
check_wallet = "one1prz9j6c406h6uhkyurlx9yq9h2e2zrpasr2saf"


def get_validator_voting_info(
    fn: str,
    vote_address_args: str,
    vote_name: str,
    grouped_data: dict,
    num_pages: int = 100,
    save_json_data: bool = False,
    check_wallet: bool = False,
) -> None:

    vote_address = gov_base.format(*vote_address_args)
    vote_address_api = snapshot_api_base.format(*vote_address_args)

    log.info(vote_address)

    voted, voted_results = call_api(vote_address_api, fn=f"{vote_name}-{fn}")
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
                choices = voted_results[eth_add]["msg"]["payload"]["choice"]
                if not isinstance(choices, dict):
                    choices = {choices: 100}

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
                            display_check = f"\n\tWallet *- {check_wallet} -* Voted NO!"

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
        "HIP16": ("staking-mainnet", "QmPp4qyickzmtJN2GQTKFHTGxEnQB583Es65VB8Rx8qws1"),
        "HIP17": ("staking-mainnet", "QmR1CoazT5suvF1zU2Dk4ZPNiF6GDKUzQkcX3ABENAHjQb"),
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
