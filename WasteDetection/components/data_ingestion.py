import os
import sys
import gdown
import zipfile
from WasteDetection.logger import logging
from WasteDetection.exception import AppException
from WasteDetection.entity.config_entity import DataIngestionConfig
from WasteDetection.entity.artifacts_entity import DataIngestionArtifact

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig = DataIngestionConfig()):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise AppException(e)
        
    def download_data(self)-> str:
        """
        Fetch data from the URL
        """

        try:
            dataset_url = self.data_ingestion_config.data_download_url
            zip_download_dir = self.data_ingestion_config.data_ingestion_dir
            os.makedirs(zip_download_dir, exist_ok=True)
            data_file_name = "waste-data-updated.zip"
            zip_file_path = os.path.join(zip_download_dir, data_file_name)
            logging.info(f"Downloading data from {dataset_url} into file {zip_file_path}")

            # Correctly extract the file ID
            file_id = dataset_url.split("/d/")[1].split("/")[0]
            logging.info(f"Extracted file ID: {file_id}")

            # Use the correct URL format for gdown
            gdown_url = f"https://drive.google.com/uc?id={file_id}"
            gdown.download(gdown_url, zip_file_path, quiet=False)
            logging.info(f"Downloaded data from {dataset_url} into file {zip_file_path}")

            return zip_file_path
        
        except Exception as e:
            raise AppException(e)
        

    def extract_zip_file(self, zip_file_path:str)->str:
        """
        zip_file_path: str
        Extracts the zip file into the data directory
        Function returns None
        """

        try:
            feature_store_path = self.data_ingestion_config.feature_store_file_path
            os.makedirs(feature_store_path, exist_ok=True)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(feature_store_path)
            logging.info(f"Extracting zip file: {zip_file_path} into dir: {feature_store_path}")

            return feature_store_path
        
        except Exception as e:
            raise AppException(e)
        

    def initiate_data_ingestion(self)-> DataIngestionArtifact:
        logging.info("Entered initiate_data_ingestion method of Data_Ingestion class")
        try:
            zip_file_path = self.download_data()
            feature_store_path = self.extract_zip_file(zip_file_path)

            data_ingestion_artifact = DataIngestionArtifact(
                data_zip_file_path=zip_file_path,
                feature_store_path=feature_store_path
            )

            logging.info("Exited initiate_data_ingestion method of Data_Ingestion class")
            logging.info(f"Data ingestion artifact: {data_ingestion_artifact}")

            return data_ingestion_artifact
        
        except Exception as e:
            raise AppException(e)