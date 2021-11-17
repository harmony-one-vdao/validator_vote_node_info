# validator_info
Gather validator information via API

Connects to various public APIs and collates data from Validators.
Creates csv of data and will also parse contact information into seperate files for ease of use.

`voting.py` and `node_version.py` will only return those validators that need to vote / update.  `weekly_metrics.py` will return all validators.

ONLY `active` validators are included in these metrics, although this can be configured to include all if required.

The following structure will be created in a new folder `data`

```
data ───│   all_validators.json
        │   data.log
        │   validator_contacts.csv       
        │
        ├───HIP15
        │       HIP15-at_only.txt
        │       HIP15-discord.txt
        │       HIP15-email.txt
        │       HIP15-facebook.txt
        │       HIP15-reddit.txt
        │       HIP15-telegram.txt
        │       HIP15-twitter.txt
        │       HIP15-unknown.txt
        │       HIP15-validator_vote.csv
        │       HIP15-voting_stats.csv
        │       HIP15-website.txt
        │
        ├───v4.3.0
        │       v4.3.0-at_only.txt
        │       v4.3.0-discord.txt
        │       v4.3.0-email.txt
        │       v4.3.0-facebook.txt
        │       v4.3.0-reddit.txt
        │       v4.3.0-telegram.txt
        │       v4.3.0-twitter.txt
        │       v4.3.0-unknown.txt
        │       v4.3.0-website.txt
        │       validator_node_versions.csv
        │
        └───Weekly-Metrics
                Weekly_metrics_17-11-21.csv
```
# install
`sudo apt update && sudo apt upgrade -y`

`apt install python3-pip`

`pip3 install -r requirements.txt`


# Configure & Run Scripts

> configure node version

1. update node version
2. add a wallet to check (Optional)

``` python 

latest_node_version = "v7174-v4.3.0-0-g15f9b2d1"

# check a single wallets Node version.
check_wallet = "one1prz9j6c406h6uhkyurlx9yq9h2e2zrpasr2saf"

```
> run node_version

`python3 node_version.py`

// terminal display also included in `data/data.log`

```

Node Version: v4.3.0

        Number Active Validators           ::  229
        Has Updated to latest version      ::  186
        Not Updated to latest version      ::  43

        Has Updated to latest version %    ::  81.22 %
        Not Updated to latest version %    ::  18.78 %


        Number Elected Validators          ::  155
        Has Updated & Elected              ::  150
        Not Updated & Elected              ::  5

        Has Updated & Elected %            ::  96.77 %
        Not Updated & Elected %            ::  3.23 %

        Wallet *- one199wuwepjjefwyyx8tc3g74mljmnnfulnzf7a6a -* Node Updated = YES!
        Node Version(s) = ['v7174-v4.3.0-0-g15f9b2d1']

```

> Check `data/<NODE_VERSION>/` folder for info.


> configure voting

1. Add a wallet to check (Optional)
2. Add the vote(s) name and Snapshot ID to the dict at the bottom of the voting.py
   

``` python
votes_to_check = {
        "HIP14": vote_api_staking_mainnet.format(
            "QmXemgh9rm578TBbUTFXRh9KkxkvVJmEDCTgRfN7ymgAtN"
        ),
        "HIP15": vote_api_staking_mainnet.format(
            "QmewxBWGsDNAMTC4q6DAzPwUkSLDpjDAqBc6JuTTZiA2D4"
        ),
        "<VOTE NAME>": vote_api_staking_mainnet.format(
            "<SNAPSHOT VOTE ID>"
        ),
    }
```

``` python
# check a single wallets vote
check_wallet = "one1prz9j6c406h6uhkyurlx9yq9h2e2zrpasr2saf"
```

> Run script
`python3 voting.py`

// terminal display also included in `data/data.log`
```
HIP15

        Total Stake           ::  4,551,028,922

Weights

        Yes Vote Weight       ::  3,121,416,827
        No Vote Weight        ::  3,831,211
        Abstain Vote Weight   ::  0
        Total Vote Weight     ::  3,125,248,038

Percentages

        Yes Vote %            ::  68.59 %
        No Vote %             ::  0.08 %
        Abstain Vote %        ::  0.0 %
        Total Vote %          ::  68.67 %

Quorum

        51 % of total         ::  2,321,024,750
        weight to make 51%    ::  -804,166,811
        % to make 51%         ::  -17.67 %

Binance & Kucoin

        Binance & Kucoin      ::  405,218,015
        Binance Kucoin %      ::  8.9 %
        Weight left No B & K  ::  1,020,562,869
        % left No B&K         ::  22.43 %

Binance Controlled Stake

        Binance Control       ::  1,631,738,444
        Binance Control %     ::  35.85 %

Snapshot

        Vote Address          ::  https://snapshot.hmny.io/api/staking-mainnet/proposal/QmewxBWGsDNAMTC4q6DAzPwUkSLDpjDAqBc6JuTTZiA2D4


        Wallet *- one1prz9j6c406h6uhkyurlx9yq9h2e2zrpasr2saf -* Voted Yes!


```

> Check `data/<VOTING_NAME>/` folder for info

# Create weekly metrics

> run the script - No terminal data display.

`python3 weekly_metrics.py`

> check folder `data/Weekly-Metrics/`

