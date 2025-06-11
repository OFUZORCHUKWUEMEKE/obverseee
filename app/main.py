from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.database import init_db
from bot.bot import start_bot,stop_bot
import logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logging.info("Starting up FastAPI application...")
    await start_bot()
    await init_db()
    logging.info("FastAPI application started successfully")
    logging.info("MongoDB database connected successfully")
    
    yield
    
    # Shutdown
    logging.info("Shutting down FastAPI application...")
    await stop_bot()
    logging.info("FastAPI application shut down successfully")


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}