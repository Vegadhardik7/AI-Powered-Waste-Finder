import os, sys
import shutil
from WasteDetection.logger import logging
from WasteDetection.exception import AppException
from WasteDetection.entity.config_entity import DataValidationConfig
from WasteDetection.entity.artifacts_entity import (DataIngestionArtifact, DataValidationArtifact)

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
        except Exception as e:
            raise AppException(e)
        
    def validate_all_file_exist(self) -> bool:
        """
        Validates that all required files exist in the feature store directory.
        """
        try:
            # Get the list of all files in the feature store directory
            all_files = os.listdir(self.data_ingestion_artifact.feature_store_path)
            
            # Check for missing files
            missing_files = [file for file in self.data_validation_config.required_file_list if file not in all_files]

            # Determine validation status
            validate_status = len(missing_files) == 0

            # Create the validation directory if it doesn't exist
            os.makedirs(self.data_validation_config.data_validation_dir, exist_ok=True)

            # Write validation status and missing files (if any) to the status file
            with open(self.data_validation_config.valid_status_file_dir, 'w') as f:
                f.write(f"Validation Status: {validate_status}\n")
                if not validate_status:
                    f.write(f"Missing Files: {', '.join(missing_files)}\n")

            return validate_status

        except Exception as e:
            raise AppException(e)
        
    def initiate_data_validation(self)-> DataValidationArtifact:
        logging.info("Entered initiate_data_validation method of Data DataValidation class")
        try:
            status = self.validate_all_file_exist()
            data_validation_artifact = DataValidationArtifact(validation_status=status)
            logging.info("Exited initiate_data_validation method of DataValidation class")
            logging.info(f"Data validation artifact: {data_validation_artifact}")

            if status:
                shutil.copy(self.data_ingestion_artifact.data_zip_file_path, os.getcwd())
            return data_validation_artifact
        except Exception as e:
            raise AppException(e)
        
