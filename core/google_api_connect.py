from requests import Session
from csv import DictReader
import io


def download_file_from_google_drive(id: str, gid: int, *args, **kw: dict) -> None:

    URL = f"https://docs.google.com/spreadsheets/d/{id}/export?format=csv&id={id}&gid={gid}"

    session = Session()

    response = session.get(URL, params={"id": id}, stream=True,)
    token = get_confirm_token(response)

    if token:
        params = {"id": id, "confirm": token}
        response = session.get(URL, params=params, stream=True,)

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


def create_dict_from_csv(data: bytes, destination: str, save_csv: bool = False) -> dict:
    rtn_list = []

    csv_decoded = io.StringIO(data.decode("utf-8"))
    reader = DictReader(csv_decoded)
    for row in reader:
        rtn_list.append(row)

    if save_csv:
        with open(destination, "wb") as f:
            f.write(data)

    return rtn_list


if __name__ == "__main__":
    file_id = r"1i6pG4odOvS-CP-83WpzE4Yzaqw_fF1Dlav1lPWOzvow"
    gid = "864212071"
    destination = "validator_contacts.csv"
    csv_dicts = download_file_from_google_drive(
        file_id, gid, destination, save_csv=True
    )

    print(csv_dicts)
