import json
import psycopg2

from abc import ABC, abstractmethod
from psycopg2.extras import execute_values


class MountainExporter(ABC):
    """
    Responsible for loading data into the database
    """
    def __init__(
            self,
            username: str,
            password: str,
            host: str,
            port: str,
            database: str,
            dataType: str,
            chunkSize: int = 200) -> None:
        """
        :param username: Postgres username
        :param password: Postgres password
        :param host: Postgres host
        :param port: Postgres port
        :param database: Postgres database
        :param dataType: The type of data that is being uploaded (e.g. areas, area comments, routes, etc)
        :param chunkSize: Number of rows to insert at a time
        """
        self.dataType = dataType
        self.chunkSize = chunkSize
        self.connection = psycopg2.connect(
            user=username,
            password=password,
            host=host,
            port=port,
            database=database
        )

        self.cursor = self.connection.cursor()

    @property
    @abstractmethod
    def query(self):
        raise NotImplementedError

    def postToSQL(self, file: str, commit: bool = False) -> None:
        """
        Export the passed file to SQL

        :param file: File containing the data to export
        :param commit: Boolean commit flag
        """
        with open(file, "r") as f:
            for lineNumber, line in enumerate(f):
                if lineNumber % self.chunkSize == 0:
                    if lineNumber > 0:
                        execute_values(self.cursor, self.query, data)

                    data = list()
                data.append(tuple(json.loads(line).values()))

            # Upload any leftovers
            if data:
                execute_values(self.cursor, self.query, data)

        if commit:
            self.connection.commit()
        else:
            self.connection.rollback()