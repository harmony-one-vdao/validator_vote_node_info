import os, sys

sys.path.append(os.path.dirname("."))
from core.util import *


def smartstake_base(
    token: str, _type: str = "listPools", method: str = "status=AllEligible"
) -> dict:

    url = f"https://hprod.smartstakeapi.com/listData?type={_type}&{method}&key=2mwTEDr9zXJH323M&token={token}&app=HARMONY"
    ss_get = get(url)
    ss_status = ss_get.status_code

    if ss_status != 200:
        raise Exception(f"Unable to connect {ss_status}  ::  {ss_get.text}")

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
    except TypeError:
        # log.info("Smartstake Token Not Valid.  Please obtain a new one")
        return "N/A", "N/A"


if __name__ == "__main__":
    token = "1634037"
    res, msg = smartstake_base(token)

    log.info(f"{res}  {msg}")
