import os, sys

sys.path.append(os.path.dirname(__file__))

from core.one_to_eth import convert_one_to_hex
from includes.blacklist import blacklist, updated_but_vers_not_found
from core.smartstake_connect import find_smartstakeid, smartstake_base

external_nodes_weight = 51 # %
internal_nodes_weight = 49 # %
combined_voting_power_min = 66.66 # %

vote_quorum = 51

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

smartstake_validator_list_fn = os.path.join("examples", "validator_list")
smartstake_address_summary = "https://harmony.smartstake.io/val/{}"
smartstake_address_blskeys = "https://harmony.smartstake.io/keys/{}"
smartstake_token = "1634037654"
res, smartstake_validator_list = smartstake_base(smartstake_token)

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
