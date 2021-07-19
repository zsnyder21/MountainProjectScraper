import psycopg2
from psycopg2.extras import execute_values

import json
import os
import typing
from dotenv import load_dotenv


class MountainExporter(object):
    def __init__(self, username: str, password: str, host: str, port: str, database: str, file: str, dataType: str,
                 chunkSize: int = 200):
        self.file = file
        self.dataType = dataType
        self.chunkSize = chunkSize

        if dataType.upper() not in {"Areas".upper(), "AreaComments".upper(), "Routes".upper(), "RouteComments".upper(),
                                    "RouteTicks".upper()}:

            raise ValueError(f"Invalid value specified for parameter dataType: {dataType}."
                             f" Allowed values are [Areas, AreaComments, Routes, RouteComments, RouteTicks].")

        self.connection = psycopg2.connect(user=username,
                                           password=password,
                                           host=host,
                                           port=port,
                                           database=database)

        self.cursor = self.connection.cursor()

    def postToSQL(self):
        if self.dataType.upper() == "Areas".upper():
            self.postAreasToSQL()
        elif self.dataType.upper() == "AreaComments".upper():
            self.postAreaCommentsToSQL()
        elif self.dataType.upper() == "Routes".upper():
            self.postRoutesToSQL()
        elif self.dataType.upper() == "RouteComments".upper():
            self.postRouteCommentsToSQL()
        elif self.dataType.upper() == "RouteTicks".upper():
            self.postRouteTicksToSQL()
        else:
            pass

        self.connection.close()

    def postAreasToSQL(self) -> None:
        insertAreaQuery = """
            INSERT INTO Areas (
                AreaId,
                ParentAreaId,
                AreaName,
                Elevation,
                ElevationUnits,
                Latitude,
                Longitude,
                ViewsMonth,
                ViewsTotal,
                SharedOn,
                Overview,
                Description,
                GettingThere,
                URL
                )
            VALUES %s;
            """

        file = open(self.file, "r")
        self.sendDataToSQL(file, insertAreaQuery)
        file.close()
        self.connection.commit()

    def postAreaCommentsToSQL(self) -> None:
        insertAreaCommentsQuery = """
            INSERT INTO AreaComments (
                CommentId,
                AreaId,
                UserId,
                UserName,
                CommentBody,
                CommentDate,
                BetaVotes,
                AdditionalInfo
                )
            VALUES %s;
            """

        file = open(self.file, "r")
        self.sendDataToSQL(file, insertAreaCommentsQuery)
        file.close()
        self.connection.commit()

    def postRoutesToSQL(self) -> None:
        insertRouteQuery = """
            INSERT INTO Routes (
                RouteId,
                AreaId,
                RouteName,
                Difficulty_YDS,
                Difficulty_French,
                Difficulty_ADL,
                Severity,
                Type,
                Height,
                HeightUnits,
                Pitches,
                Grade,
                Description,
                Location,
                Protection,
                FirstAscent,
                FirstAscentYear,
                FirstFreeAscent,
                FirstFreeAscentYear,
                AverageRating,
                VoteCount,
                URL
                )
            VALUES %s;
            """

        file = open(self.file, "r")
        self.sendDataToSQL(file, insertRouteQuery)
        file.close()
        self.connection.commit()

    def postRouteCommentsToSQL(self) -> None:
        insertRouteCommentsQuery = """
            INSERT INTO RouteComments (
                CommentId,
                RouteId,
                UserId,
                UserName,
                CommentBody,
                CommentDate,
                BetaVotes,
                AdditionalInfo
                )
            VALUES %s;
            """

        file = open(self.file, "r")
        self.sendDataToSQL(file, insertRouteCommentsQuery)
        file.close()
        self.connection.commit()

    def postRouteTicksToSQL(self):
        insertRouteTicksQuery = """
            INSERT INTO RouteTicks (
                RouteId,
                UserId,
                UserName,
                TickDate,
                TickInfo,
                URL
                )
            VALUES %s;
            """

        file = open(self.file, "r")
        self.sendDataToSQL(file, insertRouteTicksQuery)
        file.close()
        self.connection.commit()

    def sendDataToSQL(self, file: typing.IO, query: str) -> None:
        for lineNumber, line in enumerate(file):
            if lineNumber % self.chunkSize == 0:
                if lineNumber > 0:
                    execute_values(self.cursor, query, data)
                data = list()

            data.append(tuple(json.loads(line).values()))

        # Upload anything leftover
        if data:
            execute_values(self.cursor, query, data)


if __name__ == "__main__":
    load_dotenv()
    password = os.getenv("POSTGRESQL_PASSWORD")

    files = [
        ("Areas", "../data/Clean/Areas.json"),
        ("AreaComments", "../data/Clean/AreaComments.json"),
        ("Routes", "../data/Clean/Routes.json"),
        ("RouteComments", "../data/Clean/RouteComments.json"),
        ("RouteTicks", "../data/Clean/RouteTicks.json")
    ]

    exporters = [
        MountainExporter(username="postgres",
                         password=password,
                         host="127.0.0.1",
                         port="5432",
                         database="MountainProject",
                         file=file,
                         dataType=dataType)
        for dataType, file in files
    ]

    for exporter in exporters:
        exporter.postToSQL()
