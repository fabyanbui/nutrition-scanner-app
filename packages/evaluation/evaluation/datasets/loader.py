import json
import os
from .schema import Dataset, Annotation

class DatasetLoader:
    def __init__(self, dataset_dir: str):
        self.dataset_dir = dataset_dir

    def load_dataset(self, annotation_file: str) -> Dataset:
        filepath = os.path.join(self.dataset_dir, annotation_file)
        with open(filepath, 'r') as f:
            data = json.load(f)
        return Dataset(**data)
