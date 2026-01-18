from fastapi import FastAPI
from app.routers import ride

app = FastAPI(title="Uber Clone API")

app.include_router(ride.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
