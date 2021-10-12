from bech32 import *
from eth_utils import *


def is_valid_address(address: str) -> bool:
    """
    Check if given string is valid one address
    NOTE: This function is NOT thread safe due to the C function used by the bech32 library.
    Parameters
    ----------
    address: str
        String to check if valid one address
    Returns
    -------
    bool
        Is valid address
    """
    if not address.startswith("one1"):
        return False
    hrp, _ = bech32_decode(address)
    if not hrp:
        return False
    return True


def convert_one_to_hex(addr: str) -> str:
    """
    Given a one address, convert it to hex checksum address
    """
    if not is_valid_address(addr):
        return to_checksum_address(addr)
    hrp, data = bech32_decode(addr)
    buf = convertbits(data, 5, 8, False)
    address = "0x" + "".join("{:02x}".format(x) for x in buf)
    return to_checksum_address(address)


if __name__ == "__main__":
    eth_add = "0x08c4596B157EafAE5EC4E0fE629005Bab2a10C3D"
    one_add = "one1prz9j6c406h6uhkyurlx9yq9h2e2zrpasr2saf"
    converted_to_eth = convert_one_to_hex(one_add)
    log.info(converted_to_eth)
    log.info(converted_to_eth == eth_add)

    # converted_to_one = bech32_decode(eth_add)
    # log.info(converted_to_one)
    # log.info(converted_to_one == one_add)
