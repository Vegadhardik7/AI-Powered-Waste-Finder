import os
import sys
import gdown
import shutil
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
        
    def download_data(self) -> str:
        """
        Fetch data from the URL, extract it, and move contents into feature_store folder.
        Avoids redundant downloads or extractions.
        """
        try:
            dataset_url = self.data_ingestion_config.data_download_url
            zip_download_dir = self.data_ingestion_config.data_ingestion_dir
            os.makedirs(zip_download_dir, exist_ok=True)

            data_file_name = "waste-data-updated.zip"
            zip_file_path = os.path.join(zip_download_dir, data_file_name)
            feature_store_dir = os.path.join(zip_download_dir, "feature_store")
            extracted_folder = os.path.join(zip_download_dir, "waste-data-updated")

            # Skip download if ZIP file already exists
            if not os.path.exists(zip_file_path):
                logging.info(f"Downloading data from {dataset_url} into file {zip_file_path}")
                file_id = dataset_url.split("/d/")[1].split("/")[0]
                gdown_url = f"https://drive.google.com/uc?id={file_id}"
                gdown.download(gdown_url, zip_file_path, quiet=False)
                logging.info(f"Downloaded data into: {zip_file_path}")
            else:
                logging.info(f"ZIP file already exists at: {zip_file_path}, skipping download.")

            # Extract if folder doesn't already exist
            if not os.path.exists(extracted_folder):
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(zip_download_dir)
                    logging.info(f"Extracted zip file to: {zip_download_dir}")
            else:
                logging.info(f"Extraction folder already exists at: {extracted_folder}, skipping extraction.")

            # Create feature_store dir if not exists
            os.makedirs(feature_store_dir, exist_ok=True)

            # Move contents if not already moved
            if os.path.exists(extracted_folder):
                for item in os.listdir(extracted_folder):
                    source_path = os.path.join(extracted_folder, item)
                    dest_path = os.path.join(feature_store_dir, item)
                    if not os.path.exists(dest_path):  # prevent overwrite
                        shutil.move(source_path, dest_path)
                        logging.info(f"Moved: {item} → {feature_store_dir}")
                    else:
                        logging.info(f"Skipped moving {item}, already exists in feature_store.")
                # Remove extracted_folder after move
                shutil.rmtree(extracted_folder)
                logging.info(f"Removed folder: {extracted_folder}")
            else:
                logging.info(f"No extracted folder found at: {extracted_folder}, skipping move.")

            # Clean redundant inner folder if somehow created
            redundant_folder = os.path.join(feature_store_dir, "waste-data-updated")
            if os.path.exists(redundant_folder):
                shutil.rmtree(redundant_folder)
                logging.info(f"Removed redundant folder: {redundant_folder}")

            # Modify the content of data.yaml
            data_yaml_path = os.path.join(feature_store_dir, "data.yaml")
            if os.path.exists(data_yaml_path):
                with open(data_yaml_path, 'w') as yaml_file:
                    yaml_file.write("train: ../artifacts/data_ingestion/feature_store/train/images\n")
                    yaml_file.write("val: ../artifacts/data_ingestion/feature_store/valid/images\n")
                    yaml_file.write("nc: 2\n")
                    yaml_file.write("names: ['glass', 'metal']\n")
                logging.info(f"Modified content of data.yaml at: {data_yaml_path}")

            # Make a copy of data.yaml in the current directory
            if os.path.exists(data_yaml_path):
                shutil.copy(data_yaml_path, "./")
                logging.info(f"Copied data.yaml to current directory.")

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