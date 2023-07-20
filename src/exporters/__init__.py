from src.exporters.MountainProjectExporter import MountainExporter
from src.exporters.areas import AreasExporter, AreaCommentsExporter
from src.exporters.routes import (
    RouteCommentsExporter,
    RouteRatingsExporter,
    RouteStarRatingsExporter,
    RouteTicksExporter,
    RouteToDosExporter,
    RoutesExporter
)
from src.exporters.reference import DifficultyReferenceExporter, SeverityReferenceExporter

factoryMap = {
    "AREACOMMENTS": AreaCommentsExporter,
    "AREAS": AreasExporter,
    "ROUTECOMMENTS": RouteCommentsExporter,
    "ROUTESTARRATINGS": RouteStarRatingsExporter,
    "ROUTERATINGS": RouteRatingsExporter,
    "ROUTETICKS": RouteTicksExporter,
    "ROUTETODOS": RouteToDosExporter,
    "ROUTES": RoutesExporter,
    "DIFFICULTYREFERENCE": DifficultyReferenceExporter,
    "SEVERITYREFERENCE": SeverityReferenceExporter
}

def getExporter(dataType: str) -> type[MountainExporter]:
    """
    Takes a file name and returns the appropriate class of exporter to process that file.
    Note that this function does not instantiate an instance for you as I don't want to handle
    passing arguments in here

    :param dataType: The type of data to be processed (i.e. Areas, AreaComments, Routes, etc.)
    :return: Appropriate class of exporter to handle the passed file
    """
    return factoryMap[dataType.upper()]
