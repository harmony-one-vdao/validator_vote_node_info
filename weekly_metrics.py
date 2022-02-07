from core.common import *
from core.smartstake_connect import find_smartstakeid


def get_metrics(
    fn: str,
    num_pages: int = 100,
    save_json_data: bool = False,
) -> None:

    csv_data = []
    result = []

    res, _, validators = call_api(staking_info_url)
    if not res:
        log.error("Error Connecting, Shutting Down.. ")
        return False

    for y in yield_data(result, num_pages=num_pages):
        result, _, _, _, v, e = y
        # eth_add = convert_one_to_hex(v.address)
        staked = round(float(e.total_delegation) / places)
        try:
            ss_address, _ = find_smartstakeid(v.address, smartstake_validator_list)
        except TypeError:
            continue

        uptime_percentage = uptime(v, validators)
        created_dt, created_str = time_of_block(v.creation_height)
        months = months_between_dates(created_dt)
        band = find_weight_range(int(staked))

        if e.active_status == "active":
            w = {
                "Name": v.name,
                "Address": v.address,
                "Staked": f"{staked:,}",
                "Epos Status": e.epos_status,
                "Active Status": e.active_status,
                "Weekly Uptime": f"{uptime_percentage}%",
                "Created ": created_str,
                "Months": months,
                "Band": band,
                "Smartstake Summary": ss_address,
            }

            csv_data.append(w)

    save_csv(
        metrics_folder,
        f"{fn}.csv",
        csv_data,
        [x for x in csv_data[0].keys()],
    )

    # display_stats = None

    # save_and_display(
    #     fn,
    #     result,
    #     None,
    #     display_stats,
    #     display_vote_stats,
    #     save_json_data=save_json_data,
    # )


if __name__ == "__main__":
    metrics_folder = "Weekly-Metrics"
    create_folders_change_handler(metrics_folder)
    get_metrics(
        metrics_fn,
        num_pages=100,
        save_json_data=True,
    )
