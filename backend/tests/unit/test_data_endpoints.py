"""
Unit tests for data API endpoints

Tests CRUD operations and query functionality.

Location: backend/tests/unit/test_data_endpoints.py
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch

from backend.api.routes.data import (
    CreateRequest,
    DeleteRequest,
    ReadRequest,
    UpdateRequest,
    create_record,
    delete_record,
    query_data,
    read_records,
    update_record,
    DateRangeRequest
)


class TestCreateEndpoint:
    """Test suite for create endpoint"""

    @pytest.mark.asyncio
    async def test_create_record_success(self):
        """Test successful record creation"""
        request = CreateRequest(
            table_name="personal_data",
            data={
                "date": "2025-01-15",
                "sleep_index": 85,
                "heart_rate": 65
            }
        )

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = True
            mock_instance.create.return_value = True
            mock_processor.return_value = mock_instance

            response = await create_record(request)

            assert response.success is True
            mock_instance.connect.assert_called_once()
            mock_instance.create.assert_called_once()
            mock_instance.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_record_connection_failure(self):
        """Test create with connection failure"""
        request = CreateRequest(
            table_name="personal_data",
            data={"date": "2025-01-15"}
        )

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = False
            mock_processor.return_value = mock_instance

            with pytest.raises(Exception):
                await create_record(request)

    @pytest.mark.asyncio
    async def test_create_record_handles_null_values(self):
        """Test create properly handles null values"""
        request = CreateRequest(
            table_name="personal_data",
            data={
                "date": "2025-01-15",
                "sleep_index": None,
                "heart_rate": 65
            }
        )

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = True
            mock_instance.create.return_value = True
            mock_processor.return_value = mock_instance

            response = await create_record(request)

            assert response.success is True
            call_args = mock_instance.create.call_args
            assert call_args[1]['data']['sleep_index'] is None


class TestDeleteEndpoint:
    """Test suite for delete endpoint"""

    @pytest.mark.asyncio
    async def test_delete_record_success(self):
        """Test successful record deletion"""
        request = DeleteRequest(
            table_name="personal_data",
            criteria={"date": "2025-01-15"}
        )

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = True
            mock_instance.delete.return_value = True
            mock_processor.return_value = mock_instance

            response = await delete_record(request)

            assert response.success is True
            mock_instance.delete.assert_called_once()


class TestQueryDataEndpoint:
    """Test suite for query_data endpoint"""

    @pytest.mark.asyncio
    async def test_query_data_with_date_range(self):
        """Test query with date range"""
        request = DateRangeRequest(
            table_name="personal_data",
            start_date="2025-01-01",
            end_date="2025-01-31"
        )

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = True

            import pandas as pd
            mock_df = pd.DataFrame([
                {"date": "2025-01-15", "sleep_index": 85},
                {"date": "2025-01-16", "sleep_index": 90}
            ])
            mock_instance.execute_query.return_value = mock_df
            mock_processor.return_value = mock_instance

            response = await query_data(request)

            assert response.success is True
            assert response.row_count == 2
            assert len(response.columns) > 0

    @pytest.mark.asyncio
    async def test_query_data_without_date_range(self):
        """Test query without date range"""
        request = DateRangeRequest(table_name="personal_data")

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = True

            import pandas as pd
            mock_df = pd.DataFrame([{"date": "2025-01-15", "sleep_index": 85}])
            mock_instance.read.return_value = mock_df
            mock_processor.return_value = mock_instance

            response = await query_data(request)

            assert response.success is True
            assert response.row_count == 1

    @pytest.mark.asyncio
    async def test_query_data_empty_result(self):
        """Test query with no results"""
        request = DateRangeRequest(
            table_name="personal_data",
            start_date="9999-12-01",
            end_date="9999-12-31"
        )

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = True

            import pandas as pd
            mock_df = pd.DataFrame()
            mock_instance.execute_query.return_value = mock_df
            mock_processor.return_value = mock_instance

            response = await query_data(request)

            assert response.success is True
            assert response.row_count == 0
            assert len(response.data) == 0


class TestReadEndpoint:
    """Test suite for read endpoint"""

    @pytest.mark.asyncio
    async def test_read_records_success(self):
        """Test successful record reading"""
        request = ReadRequest(
            table_name="personal_data",
            criteria={"date": "2025-01-15"}
        )

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = True

            import pandas as pd
            mock_df = pd.DataFrame([{
                "date": "2025-01-15",
                "sleep_index": 85,
                "heart_rate": 65
            }])
            mock_instance.read.return_value = mock_df
            mock_processor.return_value = mock_instance

            response = await read_records(request)

            assert response.success is True
            assert len(response.data) == 1
            assert response.data[0]["date"] == "2025-01-15"

    @pytest.mark.asyncio
    async def test_read_records_with_columns(self):
        """Test read with specific columns"""
        request = ReadRequest(
            table_name="personal_data",
            columns=["date", "sleep_index"]
        )

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = True

            import pandas as pd
            mock_df = pd.DataFrame([{
                "date": "2025-01-15",
                "sleep_index": 85
            }])
            mock_instance.read.return_value = mock_df
            mock_processor.return_value = mock_instance

            response = await read_records(request)

            assert response.success is True
            assert len(response.data[0].keys()) == 2

    @pytest.mark.asyncio
    async def test_read_records_empty_result(self):
        """Test read with no matching records"""
        request = ReadRequest(
            table_name="personal_data",
            criteria={"date": "9999-12-31"}
        )

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = True

            import pandas as pd
            mock_df = pd.DataFrame()
            mock_instance.read.return_value = mock_df
            mock_processor.return_value = mock_instance

            response = await read_records(request)

            assert response.success is True
            assert len(response.data) == 0


class TestUpdateEndpoint:
    """Test suite for update endpoint"""

    @pytest.mark.asyncio
    async def test_update_record_success(self):
        """Test successful record update"""
        request = UpdateRequest(
            table_name="personal_data",
            data={"sleep_index": 90},
            criteria={"date": "2025-01-15"}
        )

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = True
            mock_instance.update.return_value = True
            mock_processor.return_value = mock_instance

            response = await update_record(request)

            assert response.success is True
            mock_instance.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_record_handles_null_values(self):
        """Test update properly handles null values"""
        request = UpdateRequest(
            table_name="personal_data",
            data={"sleep_index": None},
            criteria={"date": "2025-01-15"}
        )

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = True
            mock_instance.update.return_value = True
            mock_processor.return_value = mock_instance

            response = await update_record(request)

            assert response.success is True
            call_args = mock_instance.update.call_args
            assert call_args[1]['data']['sleep_index'] is None

    @pytest.mark.asyncio
    async def test_update_record_multiple_fields(self):
        """Test update with multiple fields"""
        request = UpdateRequest(
            table_name="personal_data",
            data={
                "sleep_index": 90,
                "heart_rate": 70,
                "steps": 10000
            },
            criteria={"date": "2025-01-15"}
        )

        with patch('backend.api.routes.data.DatabaseDataProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.connect.return_value = True
            mock_instance.update.return_value = True
            mock_processor.return_value = mock_instance

            response = await update_record(request)

            assert response.success is True
            call_args = mock_instance.update.call_args
            assert len(call_args[1]['data']) == 3
