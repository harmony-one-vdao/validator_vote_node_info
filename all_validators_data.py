from core.common import *
from core.smartstake_connect import find_smartstakeid


def get_validator_voting_info(
    fn: str,
    grouped_data: dict,
    num_pages: int = 100,
    save_json_data: bool = False,
) -> None:

    csv_data = []
    result = []

    for y in yield_data(result, check_wallet=False, num_pages=num_pages):
        result, _, _, _, v, e = y
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
            grouped_data[app] += grouped
            w.update({"Group": app})

            if w["Name"] not in [x["Name"] for x in csv_data]:
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
        fn,
        f"{fn}.csv",
        csv_data,
        [x for x in csv_data[0].keys()],
    )

    save_and_display(
        fn,
        result,
        grouped_data,
        None,
        None,
        save_json_data=save_json_data,
    )


if __name__ == "__main__":

    fn = "All_validators_data"
    create_folders_change_handler("all_validators_data")
    get_validator_voting_info(fn, grouped_data, num_pages=100, save_json_data=True)
