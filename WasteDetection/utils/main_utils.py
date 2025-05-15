import sys
import yaml
import base64
import os.path
from WasteDetection.logger import logging
from WasteDetection.exception import AppException

def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, 'rb') as yaml_file:
            logging.info("Read YAML file successfully!")
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise AppException(e) from e
    
def write_yaml_file(file_path: str, content: object, replace:bool = False) -> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as file:
            yaml.dump(content, file)
            logging.info("Successfully write_yaml_file")
    except Exception as e:
        raise AppException(e)
    
def decodeImage(imgstr, filename):
    imgdata = base64.b64decode(imgstr)
    with open("./data/"+filename, 'wb') as f:
        f.write(imgdata)
        f.close()

def encodeImageIntoBase64(croppedImgPath):
    with open(croppedImgPath, 'rb') as f:
        return base64.b64decode(f.read())