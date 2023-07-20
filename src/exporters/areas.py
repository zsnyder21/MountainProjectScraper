from src.exporters.MountainProjectExporter import MountainExporter


class AreasExporter(MountainExporter):
    @property
    def query(self):
        return"""
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


class AreaCommentsExporter(MountainExporter):
    @property
    def query(self):
        return """
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