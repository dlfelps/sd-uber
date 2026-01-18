from redis.asyncio import Redis

class LocationService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.geo_key = "driver_locations"

    async def update_location(self, driver_id: int, lat: float, long: float):
        """
        Updates the driver's location in Redis using GEOADD.
        Redis expects: (longitude, latitude, member)
        """
        await self.redis.geoadd(self.geo_key, (long, lat, str(driver_id)))

    async def find_nearby_drivers(self, lat: float, long: float, radius_km: float):
        """
        Finds drivers within the specified radius using GEOSEARCH.
        Returns a list of driver IDs.
        """
        # Note: Redis-py's geosearch returns a list of members.
        # We assume basic return; for more details like distance, we'd add withdist=True
        members = await self.redis.geosearch(
            name=self.geo_key,
            latitude=lat,
            longitude=long,
            radius=radius_km,
            unit="km"
        )
        return [int(member) for member in members]
