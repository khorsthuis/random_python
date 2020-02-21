import json
from pathlib import Path
from google.cloud import storage


class DownloadDecryptStore:
    """
    This class holds the method that are required to download a new google-authentication file.
    The following steps are executed to achieve this goal:
        - Read in required data from config.json
        - Downloads and saves encrypted file from google storage bucket
        - Decrypts the downloaded file and saves it under downloaded-key/gcp-key.json
    If the user has set his/her environmental variable GOOGLE_APPLICATION_CREDENTIALS to point to
    the newly downloaded file, he/she is able to use it for another day
    """
    def __init__(self):
        """Constructor for object DeleteRenewKeys that reads content from config.json """

        # open json config file that reads in information
        config_path = open("config.json", "r")
        config_json = config_path.read()
        config_dict = json.loads(config_json)

        # assign object variables
        self.project_id = config_dict["project-id"]
        self.bucket_name = config_dict["bucket-name"]
        self.location_id = config_dict["key-location"]
        self.key_ring_id = config_dict["key-ring-id"]
        self.crypto_key_id = config_dict["crypto-key-id"]
        self.service_account_email = config_dict["service-account-email"]

        # close the file
        config_path.close()

    def decrypt_symmetric(self, ciphertext):
        """Decrypts input ciphertext using a symmetric CryptoKey."""
        from google.cloud import kms_v1

        # Creates an API client for the KMS API.
        client = kms_v1.KeyManagementServiceClient()

        # The resource name of the CryptoKey.
        name = client.crypto_key_path_path(self.project_id, self.location_id, self.key_ring_id,
                                           self.crypto_key_id)
        # Use the KMS API to decrypt the data.
        response = client.decrypt(name, ciphertext)
        return response.plaintext

    def decrypt_from_file(self, file_path):
        """
        Method that decrypts a file using the decrypt_symmetric method and writes the output of this decryption
        to a file named gcp-key.json
        :param file_path: the filepath for the encrypted file that is to be decrypted
        """
        # open and decrypt byte file
        f = open(file_path, "rb").read()
        decrypted = self.decrypt_symmetric(f)
        json_string = decrypted.decode("utf-8")

        # write string to json file
        destination_file_name = Path("downloaded-key/gcp-key.json")
        destination_file_name.touch(exist_ok=True) # creates file if it does not yet exist
        destination_file_name.touch(exist_ok=True) # creates file if it does not yet exist
        destination_file_name.write_text(json_string)


    def download_key_from_blob(self):
        """
        Downloads key for configured service account and stores it in the folder generated-key/
        :return: the filepath for the downloaded file
        """
        source_blob_name = "generated-keys/{}".format(self.service_account_email)
        destination_name = self.service_account_email

        # generate destination folder and file if they do not yet exist
        Path("downloaded-key/").mkdir(parents=True, exist_ok=True)  # creates folder if not exists
        folder = Path("downloaded-key/")  # folder where all the newly generated keys go
        destination_file_name = folder / "{}".format(destination_name)  # file named after service-account name
        destination_file_name.touch(exist_ok=True)

        # download the file and store it locally
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

        # prints source and destination indicating successful download
        print('Encrypted key downloaded to -----> \n {}.'.format(
            source_blob_name,
            destination_file_name))

        return destination_file_name


def main():
    """main method that executes the workings of the script"""
    print("Reading from config.json")
    download_decrypt_store = DownloadDecryptStore()
    print("Downloading key from storage-bucket")
    file_path = download_decrypt_store.download_key_from_blob()
    print("Decrypting downloaded file")
    download_decrypt_store.decrypt_from_file(file_path)
    print("Completed")


main()

# dict = {"project-id": "ri-devops-sandbox",
#             "bucket-name": "koens-bucket",
#             "key-location": "europe-west4",
#             "key-ring-id": "name-of-keyring",
#             "crypto-key-id": "first-key",
#             "service-account-email": "another-service-account@ri-devops-sandbox.iam.gserviceaccount.com"}
#
# json_string = json.dumps(dict)
# print(json_string)


