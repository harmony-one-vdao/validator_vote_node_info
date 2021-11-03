from requests import Session

def download_file_from_google_drive(id, destination):

    URL = f'https://docs.google.com/spreadsheets/d/{id}/export?format=csv&id={id}&gid=0'


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

    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    chunk_list = []
    for chunk in response.iter_content(CHUNK_SIZE):
        if chunk:  # filter out keep-alive new chunks
            chunk_list.append(chunk)

    chunks = b"".join(chunk_list)

    with open(destination, "wb") as f:
        f.write(chunks)


if __name__ == "__main__":
    file_id = "1EkIQ45pnWnljSB2va7_9c7RqOrxpqZRhdJMd3I94Acs"
    destination = "validator_contacts.csv"
    download_file_from_google_drive(file_id, destination)


# response = requests.get('https://www.googleapis.com/storage/v1/<endpoint>', )

# 1G5sCS9GL8WAUjc5TJqQ1PPhXE-_dQSe2  restricted
# 0B3-1YjeaWAo2bF9DQmJlbElyUXpyZnV3RzFkMVh2dk40SWhF
# https://drive.google.com/file/d//view?usp=sharing
