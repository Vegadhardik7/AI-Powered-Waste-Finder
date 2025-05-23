import os, re
import yaml
import zipfile
import shutil
from WasteDetection.logger import logging
from WasteDetection.exception import AppException
from WasteDetection.utils.main_utils import read_yaml_file
from WasteDetection.entity.config_entity import ModelTrainerConfig
from WasteDetection.entity.artifacts_entity import ModelTrainerArtifact, DataIngestionArtifact

class ModelTrainer:
    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
        data_ingestion_artifact: DataIngestionArtifact
    ):
        self.model_trainer_config = model_trainer_config
        self.data_ingestion_artifact = data_ingestion_artifact

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        logging.info("Entered initiate_model_trainer method of ModelTrainer class")

        try:
            # Unzip the dataset
            logging.info("Unzipping waste-data-updated.zip")
            zip_file_path = os.path.join(self.data_ingestion_artifact.feature_store_path, "waste-data-updated.zip")
            print(f"***OLD****{zip_file_path}********")
            zip_file_path = re.sub(r'\\[^\\]+\\([^\\]+)$', r'\\\1', zip_file_path)
            print(f"***NEW****{zip_file_path}********")
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(self.data_ingestion_artifact.feature_store_path)
            os.remove(zip_file_path)

            # Define the correct path to data.yaml
            data_yaml_path = os.path.join(self.data_ingestion_artifact.feature_store_path, "data.yaml")
            
            # Check if the file exists
            if not os.path.exists(data_yaml_path):
                raise FileNotFoundError(f"data.yaml not found at {data_yaml_path}")
        
            with open(data_yaml_path, 'r') as stream:
                num_classes = str(yaml.safe_load(stream)['nc'])

            model_config_file_name = self.model_trainer_config.weight_name.split(".")[0]
            logging.info(f"Model config file name: {model_config_file_name}")

            config = read_yaml_file(f"yolov5/models/{model_config_file_name}.yaml")
            config['nc'] = int(num_classes)

            custom_model_config_path = f'yolov5/models/custom_{model_config_file_name}.yaml'
            with open(custom_model_config_path, 'w') as f:
                yaml.dump(config, f)

            # Train the model
            os.system(
                f"cd yolov5 && python train.py --img 416 --batch {self.model_trainer_config.batch_size} "
                f"--epochs {self.model_trainer_config.no_epochs} --data ../artifacts/data_ingestion/feature_store/data.yaml "
                f"--cfg ./models/custom_{model_config_file_name}.yaml --weights {self.model_trainer_config.weight_name} "
                f"--name yolov5s_results --cache"
            )

            # Copy the trained model
            best_model_path = "yolov5/runs/train/yolov5s_results/weights/best.pt"
            last_model_path = "yolov5/runs/train/yolov5s_results/weights/last.pt"

            if not os.path.exists(best_model_path):
                logging.warning(f"best.pt not found at {best_model_path}. Falling back to last.pt")
                if not os.path.exists(last_model_path):
                    raise FileNotFoundError(f"Neither best.pt nor last.pt found in {os.path.dirname(best_model_path)}")
                best_model_path = last_model_path

            shutil.copy(best_model_path, "yolov5/")
            os.makedirs(self.model_trainer_config.model_trainer_dir, exist_ok=True)
            shutil.copy(best_model_path, os.path.join(self.model_trainer_config.model_trainer_dir, "best.pt"))

            # Log the successful copy
            logging.info(f"Model copied successfully to {self.model_trainer_config.model_trainer_dir}")

            # Clean up
            shutil.rmtree("yolov5/runs", ignore_errors=True)
            shutil.rmtree("train", ignore_errors=True)
            shutil.rmtree("valid", ignore_errors=True)
            os.remove(data_yaml_path)

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path="yolov5/best.pt",
            )

            logging.info("Exited initiate_model_trainer method of ModelTrainer class")
            logging.info(f"Model trainer artifact: {model_trainer_artifact}")

            return model_trainer_artifact

        except Exception as e:
            raise AppException(e)