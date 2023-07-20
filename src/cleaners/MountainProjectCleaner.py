import json
import os

from abc import ABC, abstractmethod

class MountainCleaner(ABC):
    """
    This class is responsible for cleaning the raw MountainProject data
    """
    def __init__(self, filePath: str, dataType: str, exportDir: str):
        """
        :param filePath: File path of the data to clean
        :param dataType: The type of data to clean (i.e. Areas, Routes)
        :param exportDir: Location to export the data to
        """
        self.filePath = filePath
        self.dataType = dataType
        self.exportDir = exportDir.strip()
        self.exportDir += (r"/" if self.exportDir[-1] != r"/" else "")  # Ensure is a directory

        os.makedirs(self.exportDir, exist_ok=True)

    @abstractmethod
    def clean(self) -> None:
        """
        Cleans the data
        """
        raise NotImplementedError

    def exportToJSON(self, data: dict, dataType: str) -> None:
        """
        Export the cleaned data to a JSON file

        :param data: Data to export
        :param dataType: Type of data to export
        """
        with open(f"{self.exportDir}{dataType}.json", "a") as file:
            jsonContent = json.dumps(data, indent=None, separators=(",", ":"))
            print(jsonContent, file=file)