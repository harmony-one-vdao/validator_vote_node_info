from core.blskeys import *

latest_node_version = "v7174-v4.3.0-0-g15f9b2d1"

# check a single wallets vote
check_wallet = 'one199wuwepjjefwyyx8tc3g74mljmnnfulnzf7a6a'

def get_all_validator_info(
    fn: str, num_pages: int = 10, save_json_data: bool = False
) -> None:

    active_validators = 0
    not_updated = 0
    is_updated = 0

    elected = 0
    elected_not_updated = 0
    elected_is_updated = 0

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

    prometheus_data = get(prometheus).json()["data"]

    for i in range(0, num_pages):
        d = {
            "jsonrpc": "2.0",
            "method": "hmy_getAllValidatorInformation",
            "params": [i],
            "id": 1,
        }
        data = post(harmony_api, json=d).json()["result"]

        if not data:
            print(f"NO MORE DATA.. ENDING ON PAGE {i+1}.")
            break

        result += data

        for d in data:
            show = False
            include = False
            is_elected = False

            v, e =create_named_tuple_from_dict(d)
            if v.address == check_wallet:
                show = True


            validators = {x[0]: [] for x in csv_data}
            if not validators.get("name"):
                validators.update({v.name: []})
                include = True

            if e.active_status == "active":
                w = []
                active_validators += 1

                if e.epos_status == "currently elected":
                    elected += 1
                    is_elected = True

                for blskey in v.bls_public_keys:
                    found, msg, versions, shard = bls_key_version(
                        blskey, prometheus_data
                    )

                    # We only need to register 1 key per shard because it is the binary version not the key that require updating.
                    if shard not in validators[v.name]:
                        validators[v.name] += [shard]
                        shards = validators[v.name]

                        if (
                            include
                            and (latest_node_version not in versions)
                            and (not v.address in updated_but_vers_not_found)
                        ):
                            include = False
                            not_updated += 1
                            if show:
                                display_check = f'\n\tWallet *- {check_wallet} -* Node Updated = NO!\n'
                            if is_elected:
                                elected_not_updated += 1


                            w = [
                                v.name,
                                v.address,
                                v.security_contact,
                                v.website,
                                e.epos_status,
                                e.active_status,
                                # blskey,
                                versions,
                            ]

                        else:
                            if include:
                                include = False
                                is_updated += 1
                                if is_elected:
                                    elected_is_updated += 1
                                if show:
                                    display_check = f'\n\tWallet *- {check_wallet} -* Node Updated = YES!\n'


                if w:
                    hPoolId = find_smartstakeid(v.address, smartstake_validator_list)
                    grouped, app = sort_group(v.security_contact)
                    if app == "unknown":
                        # some validators put twitter in the website column
                        # if unknown, we can try the website column,
                        # if website == unknown, we will take the unknown from the original v.security_contact..
                        grouped, app = sort_group(v.website)
                        if app == "unknown":
                            grouped = [v.security_contact]

                    grouped_data[app] += grouped

                    w += [
                        shards,
                        app,
                        smartstake_address_summary.format(hPoolId),
                        smartstake_address_blskeys.format(hPoolId),
                    ]

                    if w not in csv_data:
                        csv_data.append(w)

    save_csv(
        fn,
        csv_data,
        [
            "Name",
            "Address",
            "Security Contact",
            "Website",
            "Epos Status",
            "Active Status",
            # "blskey",
            "version",
            "shards",
            "group",
            "Smartstake Summary",
            "Smartstake BlsKeys",
        ],
    )

    for k, v in grouped_data.items():
        save_copypasta(f"{latest_node_version.split('-')[1]}-{k}", v, **sep_map[k])

    if save_json_data:
        with open(all_validators_fn, "w") as j:
            dump(result, j, indent=4)

    display_blskey_stats(active_validators, is_updated, not_updated, elected, elected_is_updated, elected_not_updated, display_check)


if __name__ == "__main__":
    get_all_validator_info(node_version_fn, num_pages=10, save_json_data=True)
