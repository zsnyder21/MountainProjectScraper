from src.cleaners.MountainProjectCleaner import MountainCleaner
from src.cleaners.areas import AreasCleaner
from src.cleaners.routes import RoutesCleaner
from src.cleaners.ratings import RouteRatingsCleaner
from src.cleaners.stars import RouteStarRatingsCleaner
from src.cleaners.ticks import RouteTicksCleaner
from src.cleaners.todos import RouteToDosCleaner

factoryMap = {
    "AREAS": AreasCleaner,
    "ROUTES": RoutesCleaner,
    "ROUTESTARRATINGS": RouteStarRatingsCleaner,
    "ROUTERATINGS": RouteRatingsCleaner,
    "ROUTETICKS": RouteTicksCleaner,
    "ROUTETODOS": RouteToDosCleaner
}

def getCleaner(dataType: str) -> type[MountainCleaner]:
    """
    Takes a file name and returns the appropriate class of exporter to process that file.
    Note that this function does not instantiate an instance for you as I don't want to handle
    passing arguments in here

    :param dataType: The type of data to be processed (i.e. Areas, AreaComments, Routes, etc.)
    :return: Appropriate class of exporter to handle the passed file
    """
    return factoryMap[dataType.upper()]
