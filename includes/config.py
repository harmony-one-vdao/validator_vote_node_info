import os, sys
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from core.one_to_eth import convert_one_to_hex
from includes.blacklist import blacklist, updated_but_vers_not_found

places = 1000000000000000000

external_nodes_weight = 51  # %
internal_nodes_weight = 49  # %
combined_voting_power_min = 66.66  # %

vote_quorum = 51

all_validators_fn = os.path.join("data", "all_validators.json")

vote_fn = "validator_vote.csv"
metrics_fn = f'Weekly_metrics_{datetime.today().strftime("%d-%m-%y")}'

node_version_fn = "validator_node_versions.csv"
prometheus = "https://gateway.harmony.one/api/v1/metrics"

# harmony_api = "https://api.harmony.one"
# harmony_api = 'https://a.api.s0.t.hmny.io'
# harmony_api = "https://rpc.s0.t.hmny.io"
# harmony_api = 'https://api.s0.t.hmny.io/'
# harmony_api = "https://g.s0.t.hmny.io"
harmony_api = "https://rpc.hermesdefi.io/"

network_info_lite = "https://api.stake.hmny.io/networks/harmony/network_info_lite"
staking_info_url = "https://api.stake.hmny.io/networks/mainnet/validators"

snapshot_api_base = "https://snapshot.hmny.io/api/{}/proposal/{}"
gov_base = "https://gov.harmony.one/#/{}/proposal/{}"

snapshot_graph = "https://hub.snapshot.org/graphql"  # POST
snaphot_org_base = "https://snapshot.org/#/{}/proposal/{}"


smartstake_validator_list_fn = os.path.join("examples", "validator_list")
smartstake_base_url = "https://harmony.smartstake.io/"
smartstake_address_summary = "https://harmony.smartstake.io/val/{}"
smartstake_address_blskeys = "https://harmony.smartstake.io/keys/{}"


binance_wallet = "one1tvhgyvt94gkf7sqgude5tu6709kt9vg66pzwfv"

expressions = {
    "email": r"[\w\.-]+@[\w\.-]+(?:\.[\w]+)+",
    "twitter": r"^.*?\btwitter\.com/@?(\w{1,30})(?:[?/,].*)?$",
    "facebook": r"^.*?\bfacebook\.com/@?(\w{1,30})(?:[?/,].*)?$",
    "telegram": r"^.*?\bt\.me/@?(\w{1,30})(?:[?/,].*)?$",
    "discord": r"(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z0-9]+/?",
    "reddit": r"(?:https?://)?reddit\.com/?\w+/?\w+",
    "website": r"http\S+",
    "at_only": r"^.*@[\S\s]+$",
}

sep_map = {
    "email": {"end": ";"},
    "twitter": {"start": "@", "end": "\n"},
    "website": {"end": "\n"},
    "telegram": {"start": "@", "end": "\n"},
    "at_only": {"end": "\n"},
    "facebook": {"end": "\n"},
    "discord": {"end": "\n"},
    "reddit": {"end": "\n"},
    "unknown": {"end": "\n"},
}
grouped_data = {
    "email": [],
    "twitter": [],
    "facebook": [],
    "discord": [],
    "website": [],
    "reddit": [],
    "telegram": [],
    "at_only": [],
    "unknown": [],
}

# "epos-status"
# {'not eligible to be elected next epoch', 'eligible to be elected next epoch', 'currently elected'}
not_eligible_message = "not eligible to be elected next epoch"

google_file_id = r"13Lu3VVf7erkmGnOUe-I_Q-hONGGuFoKQ"
google_gid = "2130181801"
google_csv_filename = os.path.join("data", "validator_contacts.csv")
contacts_list_from_google = ("Twitter", "Reddit", "Telegram", "Facebook", "Discord")


def create_data_path(pth: str, data_path: str = "data") -> os.path:
    cwd = os.getcwd()
    p = os.path.join(cwd, data_path, pth)
    if not os.path.exists(p):
        os.mkdir(p)
    return p


create_data_path((""))

import logging

file_handler = logging.FileHandler(filename=os.path.join("data", "data.log"))
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=handlers)

log = logging.getLogger()


def create_folders_change_handler(name):
    pth = create_data_path(name)
    # TODO: Handler to change log filename..
