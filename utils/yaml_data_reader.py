import os
import yaml
import logging.config

logger = logging.getLogger(__name__)


class YAMLDataReader:

    @staticmethod
    def read_yaml_files(folder_path):
        yaml_files = [f for f in os.listdir(folder_path) if f.endswith('.yaml') or f.endswith('.yml')]
        data_list = []

        for file in yaml_files:
            with open(os.path.join(folder_path, file), 'r') as stream:
                try:
                    data = yaml.safe_load(stream)
                    data_list.append(data)
                except yaml.YAMLError as exc:
                    logger.error(f"Error processing file {file}: {exc}")

        return data_list
