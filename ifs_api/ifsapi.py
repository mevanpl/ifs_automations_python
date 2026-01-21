import requests
import base64
import os
import sys

# ----------------------------------------
# CONFIG - IFS Credentials
# ----------------------------------------
USERNAME = "SVC_RPA_DeliveryNote"
PASSWORD = "uz2wWn4xPynmV0fn1@"

BASE_URL = "https://ifsapptrain.semcomaritime.com:48080"


def get_auth_header():
    credentials = f"{USERNAME}:{PASSWORD}".encode()
    encoded = base64.b64encode(credentials).decode()
    return {"Authorization": f"Basic {encoded}"}


# ------------------------------------------------
# Step 00 - Get KeyRef using Serial No (IFS-safe)
# ------------------------------------------------
def get_keyref_by_serial(serial_no):
    # IMPORTANT:
    # IFS requires SerialNo as STRING and manual OData URL construction
    filter_query = f"SerialNo eq '{serial_no}'"

    url = (
        f"{BASE_URL}/int/ifsapplications/projection/v1/"
        "PartSerialsHandling.svc/PartSerialCatalogSet"
        f"?$filter={filter_query}&$select=keyref"
    )

    headers = {
        "Accept": "application/json",
        **get_auth_header()
    }

    print("\n Fetching KeyRef for SerialNo =", serial_no)
    print(" OData URL:", url)

    response = requests.get(url, headers=headers)

    print("Status:", response.status_code)
    print("Response:", response.text)

    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch KeyRef for SerialNo {serial_no}"
        )

    data = response.json()

    if not data.get("value"):
        raise Exception(
            f"No PartSerial found for SerialNo {serial_no}"
        )

    keyref = data["value"][0]["keyref"]

    print(" KeyRef extracted:", keyref)

    return keyref


# ------------------------------------------------
# Step 01 - Create Document
# ------------------------------------------------
def create_document(title):
    url = (
        f"{BASE_URL}/int/ifsapplications/projection/v1/"
        "CreateAndImportDocument.svc/CreateDocument"
    )

    headers = {
        "Content-Type": "application/json",
        **get_auth_header()
    }

    payload = {
        "DocClass": "TT_SER_CERIT",
        "DocNo": None,
        "DocSheet": None,
        "DocRev": None,
        "Title": title,
        "CreateFileRef": "YES"
    }

    print("\n Creating document...")

    response = requests.post(url, headers=headers, json=payload)

    print("Status:", response.status_code)
    print("Response:", response.text)

    if response.status_code != 200:
        raise Exception("CreateDocument failed!")

    data = response.json()

    return (
        data["DocClass"],
        data["DocNo"],
        data["DocSheet"],
        data["DocRev"]
    )


# ------------------------------------------------
# Step 02 - Get Upload URL
# ------------------------------------------------
def get_document_url(doc_class, doc_no, doc_sheet, doc_rev):
    url = (
        f"{BASE_URL}/int/ifsapplications/projection/v1/"
        "CreateAndImportDocument.svc/GetDocumentUrl"
    )

    headers = {
        "Content-Type": "application/json",
        **get_auth_header()
    }

    payload = {
        "DocClass": doc_class,
        "DocNo": doc_no,
        "DocSheet": doc_sheet,
        "DocRev": doc_rev
    }

    print("\n Requesting upload URL...")

    response = requests.post(url, headers=headers, json=payload)

    print("Status:", response.status_code)
    print("Response:", response.text)

    if response.status_code != 200:
        raise Exception("GetDocumentUrl failed!")

    return BASE_URL + response.json()["value"]


# ------------------------------------------------
# Step 03 - Upload File
# ------------------------------------------------
def upload_file(upload_url, file_path):
    file_name = os.path.basename(file_path)
    encoded_name = base64.b64encode(file_name.encode()).decode()

    headers = {
        "X-IFS-Content-Disposition": f"filename={encoded_name}",
        "Content-Type": "application/octet-stream",
        "If-Match": "",
        **get_auth_header()
    }

    print("\n Uploading file:", file_name)

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    response = requests.patch(upload_url, headers=headers, data=file_bytes)

    print("Status:", response.status_code)
    print("Response:", response.text)

    if response.status_code not in (200, 204):
        raise Exception("File upload failed!")

    print("\n File uploaded successfully!")


# ------------------------------------------------
# Step 04 - Connect Document to Part Serial
# ------------------------------------------------
def connect_object(doc_class, doc_no, doc_sheet, doc_rev, keyref):
    url = (
        f"{BASE_URL}/int/ifsapplications/projection/v1/"
        "CreateAndImportDocument.svc/ConnectObject"
    )

    headers = {
        "Content-Type": "application/json",
        **get_auth_header()
    }

    payload = {
        "DocClass": doc_class,
        "DocNo": doc_no,
        "DocSheet": doc_sheet,
        "DocRev": doc_rev,
        "LuName": "PartSerialCatalog",
        "KeyRef": keyref
    }

    print("\n Connecting document to Part Serial...")

    response = requests.post(url, headers=headers, json=payload)

    print("Status:", response.status_code)
    print("Response:", response.text)

    if response.status_code != 200:
        raise Exception("ConnectObject failed!")

    print("\n Document linked successfully!")


# ------------------------------------------------
# MAIN
# ------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage:")
        print('python ifsapi_v1.py "<TITLE>" "<FILE_PATH>" "<SERIAL_NO>"')
        sys.exit(1)

    title = sys.argv[1]
    file_path = sys.argv[2]
    serial_no = sys.argv[3]

    print("\n Starting IFS Document Automation")

    keyref = get_keyref_by_serial(serial_no)

    doc_class, doc_no, doc_sheet, doc_rev = create_document(title)
    upload_url = get_document_url(doc_class, doc_no, doc_sheet, doc_rev)
    upload_file(upload_url, file_path)
    connect_object(doc_class, doc_no, doc_sheet, doc_rev, keyref)

    print("\n ALL DONE!")
