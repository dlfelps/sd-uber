import typer
import asyncio
import random
from redis.asyncio import Redis
from app.services.location_service import LocationService
import os

async def simulate(driver_ids: list[int], interval: float, redis_url: str, iterations: int = None):
    """
    Simulates driver movement and updates locations in Redis.
    """
    redis_client = Redis.from_url(redis_url)
    location_service = LocationService(redis_client)
    
    # Starting points (e.g., San Francisco center)
    base_lat = 37.7749
    base_long = -122.4194
    
    # Initialize locations
    driver_locs = {did: (base_lat + random.uniform(-0.01, 0.01), 
                         base_long + random.uniform(-0.01, 0.01)) 
                   for did in driver_ids}
    
    typer.echo(f"Starting simulation for drivers: {driver_ids}")
    
    count = 0
    try:
        while iterations is None or count < iterations:
            for did in driver_ids:
                # Move slightly
                lat, lon = driver_locs[did]
                lat += random.uniform(-0.0005, 0.0005)
                lon += random.uniform(-0.0005, 0.0005)
                driver_locs[did] = (lat, lon)
                
                await location_service.update_location(did, lat, lon)
                typer.echo(f"Driver {did}: {lat:.6f}, {lon:.6f}")
            
            count += 1
            if iterations is None or count < iterations:
                await asyncio.sleep(interval)
    except asyncio.CancelledError:
        typer.echo("Simulation stopped.")
    finally:
        await redis_client.aclose()

def main(
    driver_ids: str = typer.Option("1,2,3", help="Comma-separated list of driver IDs"),
    interval: float = typer.Option(5.0, help="Update interval in seconds"),
    redis_url: str = typer.Option("redis://localhost:6379", help="Redis URL"),
    iterations: int = typer.Option(None, help="Number of iterations to run (None for infinite)")
):
    url = os.getenv("REDIS_URL", redis_url)
    ids = [int(i.strip()) for i in driver_ids.split(",")]
    asyncio.run(simulate(ids, interval, url, iterations))

if __name__ == "__main__":
    typer.run(main)
