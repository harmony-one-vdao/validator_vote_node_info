import os

all_validators_fn = os.path.join("data", "all_validators.json")

vote_address = "QmTy415weDCQd88QBaBYBSW6Ux75JiraMuyjwtSMEaEJBQ"
vote_name = "HIP-9"
vote_fn = f"validator_vote-{vote_name}.csv"

node_version_fn = "validator_node_versions.csv"
prometheus = "https://gateway.harmony.one/api/v1/metrics"

harmony_api = "https://api.harmony.one"
network_info_lite = "https://api.stake.hmny.io/networks/harmony/network_info_lite"

vote_api = "https://snapshot.hmny.io/api/dao-mainnet/proposal/{}"
vote_full_address = vote_api.format(vote_address)

binance_wallet = "one1tvhgyvt94gkf7sqgude5tu6709kt9vg66pzwfv"

expressions = {
    "email": r"[\w\.-]+@[\w\.-]+(?:\.[\w]+)+",
    "twitter": r"^.*?\btwitter\.com/@?(\w{1,30})(?:[?/,].*)?$",
    "telegram": r"^.*?\bt\.me/@?(\w{1,30})(?:[?/,].*)?$",
    "website": r"http\S+",
    "at_only": r"^.*@[\S\s]+$",
}

sep_map = {
    "email": {"end": ";"},
    "twitter": {"start": "@", "end": "\n"},
    "website": {"end": "\n"},
    "telegram": {"start": "@", "end": "\n"},
    "at_only": {"end": "\n"},
    "unknown": {"end": "\n"},
}

# "epos-status"
# {'not eligible to be elected next epoch', 'eligible to be elected next epoch', 'currently elected'}
not_eligible_message = "not eligible to be elected next epoch"

data_path = "data"


def create_data_path(data_path: str) -> None:
    cwd = os.getcwd()
    p = os.path.join(cwd, data_path)
    if not os.path.exists(p):
        os.mkdir(p)


create_data_path(data_path)
