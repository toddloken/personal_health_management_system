"""
Tests for data retrieval API endpoints

Tests the /api/data/query endpoint with various scenarios including
date range filtering, empty results, and error handling.

Location: backend/tests/test_data_routes.py
"""

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from backend.api.routes.data import router, DataResponse, DateRangeRequest
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestDataQueryEndpoint:
    """Test suite for /api/data/query endpoint"""

    @pytest.fixture
    def mock_processor(self):
        """Create a mock DatabaseDataProcessor"""
        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock:
            processor_instance = MagicMock()
            mock.return_value = processor_instance
            yield processor_instance

    @pytest.fixture
    def sample_dataframe(self):
        """Create sample DataFrame for testing"""
        return pd.DataFrame({
            'date': ['2024-11-01', '2024-11-02', '2024-11-03'],
            'sleep_hours': [7.5, 8.0, 6.5],
            'hrv': [65, 70, 68],
            'recovery_score': [85, 90, 82]
        })

    def test_query_with_date_range_success(self, mock_processor, sample_dataframe):
        """Test successful query with date range filtering"""
        mock_processor.connect.return_value = True
        mock_processor.execute_query.return_value = sample_dataframe
        mock_processor.disconnect.return_value = True

        response = client.post(
            "/api/data/query",
            json={
                "table_name": "personal_data",
                "start_date": "2024-11-01",
                "end_date": "2024-11-03"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['row_count'] == 3
        assert len(data['columns']) == 4
        assert 'date' in data['columns']
        assert len(data['data']) == 3

    def test_query_without_date_range(self, mock_processor, sample_dataframe):
        """Test query without date range (all records)"""
        mock_processor.connect.return_value = True
        mock_processor.read.return_value = sample_dataframe
        mock_processor.disconnect.return_value = True

        response = client.post(
            "/api/data/query",
            json={
                "table_name": "personal_data"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['row_count'] == 3
        mock_processor.read.assert_called_once()

    def test_query_empty_results(self, mock_processor):
        """Test query that returns no results"""
        mock_processor.connect.return_value = True
        mock_processor.execute_query.return_value = pd.DataFrame()
        mock_processor.disconnect.return_value = True

        response = client.post(
            "/api/data/query",
            json={
                "table_name": "personal_data",
                "start_date": "2024-01-01",
                "end_date": "2024-01-02"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['row_count'] == 0
        assert data['columns'] == []
        assert data['data'] == []

    def test_query_connection_failure(self, mock_processor):
        """Test handling of database connection failure"""
        mock_processor.connect.return_value = False

        response = client.post(
            "/api/data/query",
            json={
                "table_name": "personal_data",
                "start_date": "2024-11-01",
                "end_date": "2024-11-03"
            }
        )

        assert response.status_code == 500
        assert "Database connection failed" in response.json()['detail']

    def test_query_execution_error(self, mock_processor):
        """Test handling of query execution errors"""
        mock_processor.connect.return_value = True
        mock_processor.execute_query.side_effect = Exception("Query execution failed")

        response = client.post(
            "/api/data/query",
            json={
                "table_name": "personal_data",
                "start_date": "2024-11-01",
                "end_date": "2024-11-03"
            }
        )

        assert response.status_code == 500
        assert "Query execution failed" in response.json()['detail']
        mock_processor.disconnect.assert_called_once()

    def test_query_with_partial_date_range(self, mock_processor, sample_dataframe):
        """Test query with only start date provided"""
        mock_processor.connect.return_value = True
        mock_processor.read.return_value = sample_dataframe
        mock_processor.disconnect.return_value = True

        response = client.post(
            "/api/data/query",
            json={
                "table_name": "personal_data",
                "start_date": "2024-11-01"
            }
        )

        assert response.status_code == 200
        mock_processor.read.assert_called_once()

    def test_query_ensures_disconnect(self, mock_processor, sample_dataframe):
        """Test that disconnect is called even on success"""
        mock_processor.connect.return_value = True
        mock_processor.execute_query.return_value = sample_dataframe
        mock_processor.disconnect.return_value = True

        response = client.post(
            "/api/data/query",
            json={
                "table_name": "personal_data",
                "start_date": "2024-11-01",
                "end_date": "2024-11-03"
            }
        )

        assert response.status_code == 200
        mock_processor.disconnect.assert_called_once()

    def test_query_different_table(self, mock_processor, sample_dataframe):
        """Test query against different table"""
        mock_processor.connect.return_value = True
        mock_processor.read.return_value = sample_dataframe
        mock_processor.disconnect.return_value = True

        response = client.post(
            "/api/data/query",
            json={
                "table_name": "other_table"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

    def test_query_returns_none(self, mock_processor):
        """Test handling when processor returns None"""
        mock_processor.connect.return_value = True
        mock_processor.execute_query.return_value = None
        mock_processor.disconnect.return_value = True

        response = client.post(
            "/api/data/query",
            json={
                "table_name": "personal_data",
                "start_date": "2024-11-01",
                "end_date": "2024-11-03"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['row_count'] == 0

    def test_query_with_future_dates(self, mock_processor):
        """Test query with future date range"""
        mock_processor.connect.return_value = True
        mock_processor.execute_query.return_value = pd.DataFrame()
        mock_processor.disconnect.return_value = True

        future_date = (date.today() + timedelta(days=30)).isoformat()
        response = client.post(
            "/api/data/query",
            json={
                "table_name": "personal_data",
                "start_date": date.today().isoformat(),
                "end_date": future_date
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['row_count'] == 0

    def test_query_with_reversed_dates(self, mock_processor, sample_dataframe):
        """Test query where end_date is before start_date"""
        mock_processor.connect.return_value = True
        mock_processor.execute_query.return_value = pd.DataFrame()
        mock_processor.disconnect.return_value = True

        response = client.post(
            "/api/data/query",
            json={
                "table_name": "personal_data",
                "start_date": "2024-11-03",
                "end_date": "2024-11-01"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['row_count'] == 0


class TestDateRangeRequest:
    """Test suite for DateRangeRequest model"""

    def test_date_range_request_all_fields(self):
        """Test DateRangeRequest with all fields"""
        request = DateRangeRequest(
            table_name="personal_data",
            start_date="2024-11-01",
            end_date="2024-11-30"
        )
        assert request.table_name == "personal_data"
        assert request.start_date == "2024-11-01"
        assert request.end_date == "2024-11-30"

    def test_date_range_request_default_table(self):
        """Test DateRangeRequest with default table name"""
        request = DateRangeRequest()
        assert request.table_name == "personal_data"
        assert request.start_date is None
        assert request.end_date is None

    def test_date_range_request_optional_dates(self):
        """Test DateRangeRequest with only table name"""
        request = DateRangeRequest(table_name="custom_table")
        assert request.table_name == "custom_table"
        assert request.start_date is None
        assert request.end_date is None


class TestDataResponse:
    """Test suite for DataResponse model"""

    def test_data_response_creation(self):
        """Test DataResponse model creation"""
        response = DataResponse(
            success=True,
            row_count=5,
            columns=['date', 'value'],
            data=[{'date': '2024-11-01', 'value': 100}]
        )
        assert response.success is True
        assert response.row_count == 5
        assert len(response.columns) == 2
        assert len(response.data) == 1

    def test_data_response_empty_data(self):
        """Test DataResponse with empty data"""
        response = DataResponse(
            success=True,
            row_count=0,
            columns=[],
            data=[]
        )
        assert response.success is True
        assert response.row_count == 0
        assert response.columns == []
        assert response.data == []