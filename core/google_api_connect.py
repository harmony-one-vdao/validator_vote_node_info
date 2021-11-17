from requests import Session
from csv import DictReader
import io


def download_file_from_google_drive(
    id: str, google_gid: int, *args, **kw: dict
) -> None:

    URL = f"https://docs.google.com/spreadsheets/d/{id}/export?format=csv&id={id}&google_gid={google_gid}"
    print(URL)

    session = Session()

    response = session.get(
        URL,
        params={"id": id},
        stream=True,
    )
    token = get_confirm_token(response)

    if token:
        params = {"id": id, "confirm": token}
        response = session.get(
            URL,
            params=params,
            stream=True,
        )

    return save_response_content(response, *args, **kw)


def get_confirm_token(response: Session) -> str:
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    return None


def save_response_content(response: Session, *args, **kw):
    CHUNK_SIZE = 32768

    chunk_list = []
    for chunk in response.iter_content(CHUNK_SIZE):
        if chunk:  # filter out keep-alive new chunks
            chunk_list.append(chunk)

    chunks = b"".join(chunk_list)

    return create_dict_from_csv(chunks, *args, **kw)


def create_dict_from_csv(
    data: bytes, google_csv_filename: str, save_csv: bool = False
) -> dict:
    rtn_list = []

    csv_decoded = io.StringIO(data.decode("utf-8"))
    reader = DictReader(csv_decoded)
    for row in reader:
        rtn_list.append(row)

    if save_csv:
        with open(google_csv_filename, "wb") as f:
            f.write(data)

    return rtn_list


if __name__ == "__main__":
    google_file_id = r"13Lu3VVf7erkmGnOUe-I_Q-hONGGuFoKQ"
    google_gid = "2130181801"
    google_csv_filename = "validator_contacts.csv"
    google_contacts = download_file_from_google_drive(
        google_file_id, google_gid, google_csv_filename, save_csv=True
    )

    address = "one1xhwspfzgv3vh5fp9hxwngv8tvdj2qr338lmavw"
    contacts_list_from_google = ("Twitter", "Reddit", "Telegram", "Facebook", "Discord")

    for x in google_contacts:
        print(x)
        if x["address"] == address:
            d = {con: x[con] for con in contacts_list_from_google}
    print(d)

# {'Nr': '91', '# name': '君に舞い降りるピッツァ', 'Status': 'Active', 'Twitter': '', 'Reddit': '', 'Telegram': '', 'Medium': '', 'Youtube': '', 'Facebook': '', 'Discord': '', 'GitHub': '', 'website': 'https://www.1101.com/juku/hiroba/1st/free-101/03.html', 'Token': '', 'address': 'one1kq0xzzzlrpkzslwfesrgmp5e7umuxl3m3dgk27', 'Active since Block': '3366908', 'securitycontact': 'CONTACT'}
