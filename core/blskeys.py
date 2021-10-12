from core.util import *


def bls_key_version(blskey: str, epoch: int, token: str) -> tuple:
    # blskeys = ['55103630eeeb9bb9e783af0a6f6fd17a919d2adc112996be2440cd2496f170b6e00545e9cb6bf809859ef1d8bead1596']
    # bls_key_version(blskeys[0], '', '')

    # DEPRECATED

    val_page = f"https://hprod.smartstakeapi.com/listData?type=key&epoch={epoch}&blsKey={blskey}&key=2mwTEDr9zXJH323M&token={token}&app=HARMONY"

    v_get = get(val_page)
    v_status = v_get.status_code

    if v_status != 200:
        return False, f"No Key Data for Epoch {epoch}", "Version Not Found", -1
    v_data = v_get.json()

    if v_data.get("errors") or v_status != 200:
        raise Exception(f"Unable to connect {v_data}")

    v = v_data["val"]
    # name = v["name"]
    # address = v["address"]
    key_version = v_data["keyDetails"]["nodeVersion"]
    shard = v_data["keyDetails"]["shardId"]
    return True, "Key Found!", key_version, shard


def bls_key_version(blskey: str, prometheus_data: list) -> tuple:
    # hmy_consensus_bingo
    # hmy_consensus_blskeys
    # hmy_consensus_finality
    # hmy_consensus_signatures
    # hmy_consensus_sync
    # hmy_downloader_num_blocks_inserted_beacon_helper
    # hmy_node_metadata
    # hmy_p2p_consensus_msg
    # hmy_p2p_message
    # hmy_p2p_node_msg

    versions = []
    blskeys = "hmy_consensus_blskeys"
    node_meta_data = "hmy_node_metadata"
    try:
        for x in prometheus_data:
            for m in x[blskeys]["metrics"]:
                if m["labels"]["pubkey"] == blskey:
                    instance = m["labels"]["instance"]
                    shard = m["labels"]["job"].split("/v")[-1]

        for x in prometheus_data:
            for m in x[node_meta_data]["metrics"]:
                if (
                    m["labels"]["key"] == "version"
                    and m["labels"]["instance"] == instance
                ):
                    version = (
                        m["labels"]["value"].split("version")[-1].split("(")[0].strip()
                    )
                    versions.append(version)
    except UnboundLocalError:
        return False, f"No Key Data Found for {blskey}", "Version Not Found", -1

    return True, "Key Version Found", versions, shard


if __name__ == "__main__":
    blskeys = [
        "55103630eeeb9bb9e783af0a6f6fd17a919d2adc112996be2440cd2496f170b6e00545e9cb6bf809859ef1d8bead1596"
    ]
    res, msg, versions, shard = bls_key_version(
        blskeys[0], get("https://gateway.harmony.one/api/v1/metrics").json()["data"]
    )

    log.info(res, msg, versions, shard)
