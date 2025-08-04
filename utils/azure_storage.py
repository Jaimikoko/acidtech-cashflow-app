from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
import os
from flask import current_app

class AzureStorage:
    def __init__(self):
        self.connection_string = current_app.config.get('AZURE_STORAGE_CONNECTION_STRING')
        if self.connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        else:
            self.blob_service_client = None
    
    def upload_file(self, file_path, container_name, blob_name):
        if not self.blob_service_client:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, 
                blob=blob_name
            )
            
            with open(file_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error uploading to Azure Storage: {e}")
            return False
    
    def download_file(self, container_name, blob_name, download_path):
        if not self.blob_service_client:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, 
                blob=blob_name
            )
            
            with open(download_path, 'wb') as download_file:
                download_file.write(blob_client.download_blob().readall())
            
            return True
        except ResourceNotFoundError:
            current_app.logger.error(f"Blob {blob_name} not found in container {container_name}")
            return False
        except Exception as e:
            current_app.logger.error(f"Error downloading from Azure Storage: {e}")
            return False
    
    def list_blobs(self, container_name):
        if not self.blob_service_client:
            return []
        
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            blob_list = container_client.list_blobs()
            return [blob.name for blob in blob_list]
        except Exception as e:
            current_app.logger.error(f"Error listing blobs: {e}")
            return []
    
    def delete_blob(self, container_name, blob_name):
        if not self.blob_service_client:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, 
                blob=blob_name
            )
            blob_client.delete_blob()
            return True
        except ResourceNotFoundError:
            current_app.logger.error(f"Blob {blob_name} not found in container {container_name}")
            return False
        except Exception as e:
            current_app.logger.error(f"Error deleting blob: {e}")
            return False