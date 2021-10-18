from requests import get
from json import dump

prometheus = "https://gateway.harmony.one/api/v1/metrics"

prometheus_data = get(prometheus).json()["data"]

with open('prometheus_json.json', "w") as j:
    dump(prometheus_data, j, indent=4)

blskey = "03561c6e33eabc526246f3eb0c7c2d9cc3ca229458bb4034770796a530c3e5487a11b601d46910569dfaf0d2bb4ae28b"

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

res, msg, versions, shard = bls_key_version(blskey, prometheus_data)

print(res, msg, versions, shard)
# >>> True Key Version Found ['v7174-v4.3.0-0-g15f9b2d1'] 2

for i in range(0, 4):
    mainnet = f"mainnet/v{i}"
    print(int(mainnet[-1]) % 4)

print(int(blskey[-1], 16) % 4)