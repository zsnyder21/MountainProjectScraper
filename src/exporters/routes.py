from src.exporters.MountainProjectExporter import MountainExporter


class RoutesExporter(MountainExporter):
    @property
    def query(self):
        return """
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


class RouteCommentsExporter(MountainExporter):
    @property
    def query(self):
        return """
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


class RouteTicksExporter(MountainExporter):
    @property
    def query(self):
        return """
            INSERT INTO RouteTicks (
                TickId,
                RouteId,
                UserId,
                UserName,
                TickDate,
                TickInfo,
                URL
                )
            VALUES %s;
            """


class RouteStarRatingsExporter(MountainExporter):
    @property
    def query(self):
        return """
            INSERT INTO RouteStarRatings (
                RatingId,
                RouteId,
                UserId,
                UserName,
                Rating,
                URL
                )
            VALUES %s;
            """


class RouteRatingsExporter(MountainExporter):
    @property
    def query(self):
        return """
            INSERT INTO RouteRatings (
                RatingId,
                RouteId,
                UserId,
                UserName,
                Difficulty,
                Severity,
                URL
                )
            VALUES %s;
            """

class RouteToDosExporter(MountainExporter):
    @property
    def query(self):
        return """
            INSERT INTO RouteToDos (
                RouteId,
                UserId,
                UserName,
                URL
                )
            VALUES %s;
            """