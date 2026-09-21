from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation


async def set_location(loc: LocationSimulation, lat: float, lng: float) -> None:
    await loc.set(lat, lng)


async def clear_location(loc: LocationSimulation) -> None:
    await loc.clear()
