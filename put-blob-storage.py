from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os

# Azure Storage account credentials
connection_string = "<your_connection_string>"
container_name = "<your_container_name>"

# Local file path to the zip file
zip_file_path = "<path_to_your_zip_file>"
# Blob name (name of the file in the blob container)
blob_name = os.path.basename(zip_file_path)

def upload_blob():
    try:
        # Create BlobServiceClient object
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Create a new container client
        container_client = blob_service_client.get_container_client(container_name)

        # Create the container if it doesn't exist
        container_client.create_container()

        # Upload the zip file to the container
        with open(zip_file_path, "rb") as data:
            container_client.upload_blob(name=blob_name, data=data)

        print(f"Uploaded {blob_name} to {container_name} container successfully.")

    except Exception as ex:
        print("Exception:")
        print(ex)

if __name__ == "__main__":
    upload_blob()
