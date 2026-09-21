import config

from util import route

def get_route():
    with open(config.resolve_path(config.config.routeConfig), encoding='utf-8') as myFile:
        loc = route.parse_route(myFile.read())
    return loc
