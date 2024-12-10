from fastapi import APIRouter, HTTPException
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sqlalchemy import create_engine, text
import joblib
import pandas as pd

# Router for metrics
router = APIRouter()

# Database connection setup
DATABASE_URL = "postgresql://postgres:MLOPS@localhost:5432/My_Data_Base"
engine = create_engine(DATABASE_URL)

# Load the model
model = joblib.load("model/model_Bernoulli_top_features.pkl")

@router.get("/")
def get_metrics():
    try:
        # Fetch data from the database
        with engine.connect() as connection:
            query = "SELECT * FROM test_data"
            data = pd.read_sql(query, connection)

        # Split data into features (X) and target (y)
        train_columns = model.feature_names_in_
        print(train_columns)
        # Now reindex your test data with these columns
        X_test = data.drop(["raintomorrow", "id"], axis=1)


        #X_test = X_test.reindex(columns=train_columns)
        X_test = X_test.rename(columns=dict(zip(X_test.columns, train_columns)))

        y_test = data["raintomorrow"].rename("RainTomorrow")

        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average="binary"),
            "recall": recall_score(y_test, y_pred, average="binary"),
            "f1_score": f1_score(y_test, y_pred, average="binary"),
        }
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
