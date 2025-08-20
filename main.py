# API includes
import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.responses import FileResponse 

# Prometheus metrics export
from prometheus_fastapi_instrumentator import Instrumentator

# Request object and settings
from pydantic import BaseModel
from pydantic_settings import BaseSettings,SettingsConfigDict

from dumbkv import DumbKV, PostgresDumbKV

import logging
logger = logging.getLogger(__name__)

# Pydantic settings class, which allows overriding of values via environment variables
class Settings(BaseSettings):
    database_location: str = "database/dumbkv.db"
    database_type: str = "sqlite"  # Default to SQLite, can be overridden
    model_config = SettingsConfigDict(env_file=".env") # Load settings from .env file if available

class KVRequest(BaseModel):
    database: int = 0
    key: str
    value: str | None = None # Make field optional and default to empty.

# Initialize settings, API, metrics, database
settings = Settings()
api = FastAPI(
  title="DumbKV API",
  description="A simple key-value store API for demonstration purposes.",
  version="1.0.0",
  openapi_url="/openapi.json",
  docs_url="/docs",
  redoc_url=None,  # Disable ReDoc documentation
)
# Expose metrics
Instrumentator().instrument(api).expose(app=api, include_in_schema=False)

# Initialize the database connection based on the settings
if settings.database_type == "sqlite":
    dumbkv = DumbKV(settings.database_location)
elif settings.database_type == "postgres":
    dumbkv = PostgresDumbKV(settings.database_location)
else:
    raise ValueError(f"Unsupported database type: {settings.database_type}")

# UI routes
@api.get("/", include_in_schema=False)
def get_root():
  return FileResponse("ui/index.html")

@api.get("/favicon.ico", include_in_schema=False)
def get_favicon():
  return FileResponse("ui/favicon.ico")

@api.get("/health", include_in_schema=False)
def get_health():
    return {"status": "healthy"}

# KV route, POST/PUT/DELETE functions
@api.post("/kv")
async def post(request: KVRequest):
  try:
    return {"value": dumbkv.get(request.database, request.key)}
  except Exception as e:
    logger.error(f"Error retrieving value for database {request.database}: {str(e)}")
    raise HTTPException(status_code=500, detail="Internal server error")

@api.put("/kv")
async def put(request: KVRequest):
  try:
    dumbkv.set(request.database, request.key, request.value)
    return {"status": "success"}
  except Exception as e:
    if isinstance(e, HTTPException):
      raise e
    elif hasattr(e, 'message'):
      raise HTTPException(status_code=500, detail=e.message)
    logger.error(f"Error storing value for database {request.database}: {str(e)}") 
    raise HTTPException(status_code=500, detail=str(e))

@api.delete("/kv")
async def delete(request: KVRequest):
  try:
    dumbkv.delete(request.database, request.key)
    return {"status": "success"}
  except Exception as e:
    if isinstance(e, HTTPException):
      raise e
    elif hasattr(e, 'message'):
      raise HTTPException(status_code=500, detail=e.message)
    logger.error(f"Error deleting value for database {request.database}: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))


# Start uvicorn server if this script is run directly
if __name__ == "__main__":
    uvicorn.run("app.main:api", host="127.0.0.1", port=8000, reload=True)
