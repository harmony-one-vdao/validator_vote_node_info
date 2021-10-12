from core.blskeys import *

latest_node_version = "v7174-v4.3.0-0-g15f9b2d1"


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
        data = post(harmony_api, json=d).json()

        if not data["result"]:
            print(f"NO MORE DATA.. ENDING ON PAGE {i+1}.")
            break

        result += data["result"]

        for x in data["result"]:

            include = False
            is_elected = False

            v = x["validator"]

            epos_status = x["epos-status"]
            active_status = x["active-status"]

            keys = v["bls-public-keys"]
            name = v["name"]
            address = v["address"]
            contact = v["security-contact"]
            website = v["website"]

            validators = {x[0]: [] for x in csv_data}
            if not validators.get("name"):
                validators.update({name: []})
                include = True

            if active_status == "active":
                w = []
                active_validators += 1

                if epos_status == "currently elected":
                    elected += 1
                    is_elected = True

                for blskey in keys:
                    found, msg, versions, shard = bls_key_version(
                        blskey, prometheus_data
                    )

                    # We only need to register 1 key per shard because it is the binary version not the key that require updating.
                    if shard not in validators[name]:
                        validators[name] += [shard]
                        shards = validators[name]

                        if (
                            include
                            and (latest_node_version not in versions)
                            and (not address in updated_but_vers_not_found)
                        ):
                            include = False
                            not_updated += 1
                            if is_elected:
                                elected_not_updated += 1

                            w = [
                                name,
                                address,
                                contact,
                                website,
                                epos_status,
                                active_status,
                                # blskey,
                                versions,
                            ]

                        else:
                            if include:
                                include = False
                                is_updated += 1
                                if is_elected:
                                    elected_is_updated += 1
                if w:
                    hPoolId = find_smartstakeid(address, smartstake_validator_list)
                    grouped, app = sort_group(contact)
                    if app == "unknown":
                        # some validators put twitter in the website column
                        # if unknown, we can try the website column,
                        # if website == unknown, we will take the unknown from the original contact..
                        grouped, app = sort_group(website)
                        if app == "unknown":
                            grouped = [contact]

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

    display_blskey_stats(active_validators, is_updated, not_updated, elected, elected_is_updated, elected_not_updated)


if __name__ == "__main__":
    get_all_validator_info(node_version_fn, num_pages=10, save_json_data=True)
