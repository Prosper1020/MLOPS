from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# Router for data retrieval
router = APIRouter()

# Database connection setup (Replace with your actual credentials)
DATABASE_URL = "postgresql://postgres:MLOPS@localhost:5432/My_Data_Base"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a schema for response (optional)
class DataResponse(BaseModel):
    location_dartmoor: bool
    location_moree: bool
    location_waggawagga: bool
    humidity3pm: float
    temp_diff: float
    location_darwin: bool
    winddir9am_ene: bool
    raintomorrow: int
    id: int
    # Add all the necessary columns from your table

@router.get("/", response_model=list[DataResponse])
def retrieve_data(limit: int = 10):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT * FROM training_data LIMIT :limit"), {"limit": limit})
            #data = [dict(row) for row in result]
            data = [row._asdict() for row in result]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
