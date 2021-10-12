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
        return False, ss_data
    return True, ss_data


def find_smartstakeid(one_address, d: dict) -> int:
    for x in d["data"]:
        if x["address"] == one_address:
            return int(x["hPoolId"])


if __name__ == "__main__":
    token = "1634037654"
    res, msg = smartstake_base(token)

    print(res, msg)
