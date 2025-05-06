from fastapi import FastAPI
from src.api import players
from starlette.middleware.cors import CORSMiddleware

description = """
Item Management API helps with managing items in multiplayer games.
"""
tags_metadata = [
    {"name": "players", "description": "Data associated with a player."},
]

app = FastAPI(
    title="Item Management API",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Item Management API",
    },
    openapi_tags=tags_metadata,
)

origins = ["https://item-management-api-dl6u.onrender.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(players.router)

@app.get("/")
async def root():
    return {"message": "Ready for database collection!"}
