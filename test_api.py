import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import joblib

# Import your FastAPI app and routers
from main import app
from app.predict import router as predict_router
from app.metrics import router as metrics_router
from app.retrieve import router as retrieve_router, DataResponse

client = TestClient(app)

# Mock data
@pytest.fixture
def mock_db_data():
    return pd.DataFrame({
        'location_dartmoor': [True, False],
        'location_moree': [False, True],
        'location_waggawagga': [True, False],
        'humidity3pm': [80.0, 75.0],
        'temp_diff': [10.5, 8.5],
        'location_darwin': [False, True],
        'winddir9am_ene': [True, False],
        'raintomorrow': [1, 0],
        'id': [1, 2]
    })

@pytest.fixture
def mock_model():
    model = Mock()
    model.predict.return_value = np.array([True, False])
    model.feature_names_in_ = [
        'location_dartmoor', 'location_moree', 'location_waggawagga',
        'humidity3pm', 'temp_diff', 'location_darwin', 'winddir9am_ene'
    ]
    return model

# Tests for Prediction Router
    @patch('app.predict.engine')
    @patch('app.predict.model')
    def test_make_prediction_false_result(self, mock_model, mock_engine, mock_db_data):
        # Setup mock database connection and query result
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_result = Mock()
        
        # Create a row with only the required columns
        prediction_data = {
            'location_dartmoor': True,
            'location_moree': False,
            'location_waggawagga': True,
            'temp_diff': 10.5,
            'humidity3pm': 80.0,
            'location_darwin': False,
            'winddir9am_ene': True
        }
        
        mock_result.fetchone.return_value = mock_result
        mock_result._fields = list(prediction_data.keys())
        # Make the mock result return the correct values when accessed as a sequence
        mock_result.__getitem__.side_effect = lambda x: list(prediction_data.values())[x]
        
        mock_connection.execute.return_value = mock_result
        
        # Setup mock model prediction to return False
        mock_model.predict.return_value = np.array([False])
        
        # Make request
        response = client.post("/predict/?record_id=1")
        
        # Add debugging prints
        print(f"Processed data for prediction: {prediction_data}")
        
        # Assertions
        assert response.status_code == 200
        assert response.json() == {"prediction": False}
        # Verify that the model.predict was called with the correct data
        expected_data = [[v for v in prediction_data.values()]]
        mock_model.predict.assert_called_once()
        np.testing.assert_array_equal(mock_model.predict.call_args[0][0], expected_data)
    
    @patch('app.predict.engine')
    def test_make_prediction_record_not_found(self, mock_engine):
        # Setup mock to return no results
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_connection.execute.return_value = mock_result
        
        # Make request
        response = client.post("/predict/?record_id=999")
        
        # Assertions
        assert response.status_code == 404
        assert response.json()["detail"] == "Record not found"

# Tests for Metrics Router
class TestMetricsRouter:
    @patch('app.metrics.engine')
    @patch('app.metrics.model')
    def test_get_metrics_success(self, mock_model, mock_engine, mock_db_data):
        # Setup mock database connection
        mock_engine.connect.return_value.__enter__.return_value = Mock()
        
        # Setup mock data reading
        with patch('pandas.read_sql', return_value=mock_db_data):
            # Setup mock model prediction
            mock_model.predict.return_value = np.array([1, 0])
            mock_model.feature_names_in_ = mock_db_data.columns[:-2]  # Exclude raintomorrow and id
            
            # Make request
            response = client.get("/metrics/")
            
            # Assertions
            assert response.status_code == 200
            metrics = response.json()
            assert all(metric in metrics for metric in ['accuracy', 'precision', 'recall', 'f1_score'])
            assert all(0 <= metrics[metric] <= 1 for metric in metrics)

    @patch('app.metrics.engine')
    def test_get_metrics_database_error(self, mock_engine):
        # Setup mock to raise exception
        mock_engine.connect.side_effect = Exception("Database connection error")
        
        # Make request
        response = client.get("/metrics/")
        
        # Assertions
        assert response.status_code == 500
        assert "Database connection error" in response.json()["detail"]

# Tests for Data Retrieval Router
class TestDataRetrievalRouter:
    @patch('app.retrieve.engine')
    def test_retrieve_data_success(self, mock_engine, mock_db_data):
        # Setup mock database connection and query result
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        # Convert DataFrame rows to dict format that matches the API response
        mock_rows = [Mock(**row) for _, row in mock_db_data.iterrows()]
        for mock_row in mock_rows:
            mock_row._asdict.return_value = mock_db_data.iloc[mock_rows.index(mock_row)].to_dict()
        
        mock_connection.execute.return_value = mock_rows
        
        # Make request
        response = client.get("/data/?limit=2")
        
        # Assertions
        assert response.status_code == 200
        assert len(response.json()) == 2
        for item in response.json():
            assert all(field in item for field in DataResponse.__fields__)

    @patch('app.retrieve.engine')
    def test_retrieve_data_with_invalid_limit(self, mock_engine):
        # Make request with invalid limit
        response = client.get("/data/?limit=-1")
        
        # Assertions
        assert response.status_code == 200  # FastAPI automatically converts to valid integer
        mock_engine.connect.assert_called_once()

    @patch('app.retrieve.engine')
    def test_retrieve_data_database_error(self, mock_engine):
        # Setup mock to raise exception
        mock_engine.connect.side_effect = Exception("Database connection error")
        
        # Make request
        response = client.get("/data/")
        
        # Assertions
        assert response.status_code == 500
        assert "Database connection error" in response.json()["detail"]