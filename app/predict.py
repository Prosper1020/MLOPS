from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
import joblib

# Router for prediction
router = APIRouter()

# Database connection setup
DATABASE_URL = "postgresql://postgres:MLOPS@localhost:5432/My_Data_Base"
DATABASE_URL = "postgresql://postgres:MLOPS@host.docker.internal:5432/My_Data_Base"
engine = create_engine(DATABASE_URL)

# Load the model
model = joblib.load("model/model_Bernoulli_top_features.pkl")
#to remove later 

@router.post("/")
def make_prediction(record_id: int):
    try:
        with engine.connect() as connection:
            # Change the query execution to match your working Jupyter version exactly
            query = text(f"SELECT * FROM test_data WHERE id = {record_id}")
            result = connection.execute(query, {"record_id": record_id})
            # Add debugging prints
            print("Query executed")
            row = result.fetchone()
            print(f"Row fetched: {row}")
            
            if not row:
                raise HTTPException(status_code=404, detail="Record not found")

            # Get columns from result
            columns = row._fields
            print(f"Columns: {columns}")
            features = dict(zip(columns, row))
            print(f"Features: {features}")
            
            model_columns = [
                "location_dartmoor", "location_moree", "location_waggawagga",
                "temp_diff", "humidity3pm", "location_darwin", "winddir9am_ene"
            ]
            
            data = [[features[column] for column in model_columns]]
            print(f"Processed data: {data}")
            
            prediction = model.predict(data)
            return {"prediction": bool(prediction[0])}
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e)}")
        raise HTTPException(status_code=500, detail=str(e))