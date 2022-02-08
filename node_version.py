import logging
from time import sleep
from core.blskeys import *


latest_node_version = "v7331-v4.3.4-0-g4ea9072e"
                    #  v7331-v4.3.4-0-g4ea9072e-dirty

# check a single wallets Node version.
check_wallet = "one199wuwepjjefwyyx8tc3g74mljmnnfulnzf7a6a"


def validator_node_version(
    fn: str,
    latest_version: str,
    grouped_data: dict,
    num_pages: int = 100,
    save_json_data: bool = False,
    check_wallet: str = False,
) -> None:

    active_validators = 0
    not_updated = 0
    is_updated = 0

    elected = 0
    elected_not_updated = 0
    elected_is_updated = 0

    csv_data = []
    result = []

    res, _, prometheus_data = call_api(prometheus)
    if not res:
        log.error("Error Connecting, Shutting Down.. ")
        return False
    prometheus_data = prometheus_data["data"]
    display_check = f"Wallet {check_wallet} NOT Found."

    for y in yield_data(result, check_wallet=check_wallet, num_pages=num_pages):
        result, check_wallet, show, include, v, e = y

        is_elected = False

        validators = {x["Name"]: [] for x in csv_data}

        if not validators.get("Name"):
            validators.update({v.name: []})
            include = True

        if e.active_status == "active":
            w = []
            active_validators += 1

            if e.epos_status == "currently elected":
                elected += 1
                is_elected = True

            for blskey in v.bls_public_keys:
                _, _, versions, shard = bls_key_version(blskey, prometheus_data)

                # We only need to register 1 key per shard because it is the binary version not the key that require updating.
                if shard not in validators[v.name]:
                    validators[v.name] += [int(shard)]
                    shards = validators[v.name]

                    if (
                        include
                        # and (latest_node_version not in versions)
                        and ((latest_node_version not in versions) or (f'{latest_node_version}-dirty' not in versions))
                        and (not v.address in updated_but_vers_not_found)
                    ):
                        include = False
                        not_updated += 1
                        if show:
                            display_check = f"\n\tWallet *- {check_wallet} -* Node Updated = NO!\t\nNode Version(s) = {versions}\n"
                        if is_elected:
                            elected_not_updated += 1

                        w = {
                            "Name": v.name,
                            "Address": v.address,
                            "Security Contact": v.security_contact,
                            "Website": v.website,
                            "Epos Status": e.epos_status,
                            "Active Status": e.active_status,
                            # "blskey",
                            "Version": versions,
                        }

                    else:
                        if include:
                            include = False
                            is_updated += 1
                            if is_elected:
                                elected_is_updated += 1
                            if show:
                                display_check = f"\n\tWallet *- {check_wallet} -* Node Updated = YES!\n\tNode Version(s) = {versions}\n"

            if w:
                ss_address, ss_blskeys = find_smartstakeid(
                    v.address, smartstake_validator_list
                )
                grouped, app = parse_contact_info(v)
                grouped_data[app] += grouped
                w.update(
                    {
                        "Shards": shards,
                        "Group": app,
                        "Smartstake Summary": ss_address,
                        "Smartstake BlsKeys": ss_blskeys,
                    }
                )

                if w not in csv_data:
                    (
                        grouped_data,
                        social_media_contacts,
                    ) = parse_google_docs_contact_info(v, grouped_data)

                    w.update(social_media_contacts)

                    csv_data.append(w)
    save_csv(
        latest_version,
        fn,
        csv_data,
        [x for x in csv_data[0].keys()],
    )

    display_stats = (
        active_validators,
        is_updated,
        not_updated,
        elected,
        elected_is_updated,
        elected_not_updated,
        display_check,
    )
    save_and_display(
        latest_version,
        result,
        grouped_data,
        display_stats,
        display_blskey_stats,
        save_json_data=save_json_data,
    )
    return True


if __name__ == "__main__":
    latest_version = latest_node_version.split("-")[1]
    create_folders_change_handler(latest_version)
    
    c = 1
    while 1:
        log.info(f'{c}) Attempting to get data...')
        res = validator_node_version(
            node_version_fn,
            latest_version,
            grouped_data,
            num_pages=100,
            save_json_data=True,
            check_wallet=check_wallet,
        )
        if res:
            break
        else:
            log.error('Unable to connect.  sleeping for 10 seconds then retrying.. ')
            sleep(10)
        c+=1
