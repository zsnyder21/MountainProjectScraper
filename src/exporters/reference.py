from src.exporters.MountainProjectExporter import MountainExporter


class DifficultyReferenceExporter(MountainExporter):
    @property
    def query(self):
        return """
            INSERT INTO DifficultyReference (
                Difficulty,
                DifficultyRanking,
                DifficultyBucket,
                RatingSystem,
                DifficultyBucketName
                )
            VALUES %s;
        """


class SeverityReferenceExporter(MountainExporter):
    @property
    def query(self):
        return """
            INSERT INTO SeverityReference (
                Severity,
                SeverityRanking
                )
            VALUES %s;
        """