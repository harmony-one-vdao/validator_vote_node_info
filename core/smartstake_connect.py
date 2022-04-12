import os, sys

from time import time

sys.path.append(os.path.dirname("."))
from core.common import *


def smartstake_base(
    token: None = None, _type: str = "listPools", method: str = "status=AllEligible"
) -> dict:

    if not token:
        token, token_minus_1 = create_smartstake_token()

    url = f"https://hprod.smartstakeapi.com/listData?type={_type}&{method}&key=2mwTEDr9zXJH323M&token={token}&app=HARMONY"
    print(url)
    ss_get = get(url)
    ss_status = ss_get.status_code

    if ss_status != 200:
        if token:
            return False, f"Unable to connect <{ss_status}>  "
        log.info("Error with token, trying minus 1 second token")
        return smartstake_base(token=token_minus_1)

    ss_data = ss_get.json()

    if ss_data.get("errors"):
        return False, ss_data.get("errors")
    return True, ss_data


def find_smartstakeid(one_address, d: dict) -> int:
    try:
        for x in d["data"]:
            if x["address"] == one_address:
                hPoolId = int(x["hPoolId"])
                return (
                    smartstake_address_summary.format(hPoolId),
                    smartstake_address_blskeys.format(hPoolId),
                )
        return "N/A", "N/A"
    except TypeError:
        log.info("Smartstake Token Not Valid.  Please obtain a new one")
        return "N/A", "N/A"


def create_smartstake_token() -> str:
    # Call APi with normal Http to generate a token
    get(smartstake_base_url)
    # Create unix timestamp
    ts = int(time())
    # return ts and ts-1 as unix ts are each second and we might miss the 1st one.
    return str(ts), str(ts - 1)


if __name__ == "__main__":
    res, msg = smartstake_base()

    log.info(f"{res}  {msg}")
