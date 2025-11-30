"""
Data operations endpoints

Provides REST API endpoints for CRUD operations and data queries.

Location: backend/api/routes/data.py
"""

from typing import Any, Dict, List, Optional
import numpy as np

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.utils.database_processor import DatabaseDataProcessor
from backend.logger import logger

router = APIRouter(prefix="/api", tags=["data"])


class CreateRequest(BaseModel):
    data: Dict[str, Any]
    table_name: str = Field(default="personal_data")


class CreateResponse(BaseModel):
    success: bool


class DateRangeRequest(BaseModel):
    end_date: Optional[str] = None
    start_date: Optional[str] = None
    table_name: str = Field(default="personal_data")


class DataResponse(BaseModel):
    columns: list[str]
    data: list[dict]
    row_count: int
    success: bool


class DeleteRequest(BaseModel):
    criteria: Dict[str, Any]
    table_name: str = Field(default="personal_data")


class DeleteResponse(BaseModel):
    success: bool


class ReadRequest(BaseModel):
    columns: Optional[List[str]] = None
    criteria: Optional[Dict[str, Any]] = None
    limit: Optional[int] = None
    table_name: str = Field(default="personal_data")


class ReadResponse(BaseModel):
    data: List[Dict[str, Any]]
    success: bool


class UpdateRequest(BaseModel):
    criteria: Dict[str, Any]
    data: Dict[str, Any]
    table_name: str = Field(default="personal_data")


class UpdateResponse(BaseModel):
    success: bool


@router.post("/create", response_model=CreateResponse)
async def create_record(request: CreateRequest):
    """
    Create new record in database.
    Deletes existing record for the same date if it exists.

    Args:
        request: CreateRequest with table name and data

    Returns:
        CreateResponse with success status
    """
    processor = DatabaseDataProcessor()

    try:
        if not processor.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")

        data_dict = dict(request.data)

        # Map 'date' field to 'pdate' for database column
        if 'date' in data_dict:
            date_value = data_dict['date']
            data_dict['pdate'] = data_dict.pop('date')
        else:
            raise HTTPException(status_code=400, detail="Date field is required")

        # Delete existing record for this date
        processor.delete(
            criteria={'pdate': date_value},
            table_name=request.table_name
        )
        logger.info(f"Deleted existing record for date '{date_value}' if it existed")

        # Handle null/NaN values
        for key, value in data_dict.items():
            if value is None or (isinstance(value, float) and np.isnan(value)):
                data_dict[key] = None

        success = processor.create(
            data=data_dict,
            table_name=request.table_name,
            if_exists='append'
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to create record")

        logger.info(f"Created record in table '{request.table_name}' for date '{date_value}'")
        return CreateResponse(success=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create operation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        processor.disconnect()


@router.post("/data/query", response_model=DataResponse)
async def query_data(request: DateRangeRequest):
    """
    Query data from database with optional date range filtering.

    Args:
        request: Query parameters including table name and date range

    Returns:
        DataResponse with query results
    """
    processor = DatabaseDataProcessor()

    try:
        if not processor.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")

        if request.start_date and request.end_date:
            query = f"""
                SELECT * FROM {request.table_name}
                WHERE pdate >= %s AND pdate <= %s
                ORDER BY pdate
            """
            df = processor.execute_query(query, (request.start_date, request.end_date))
        else:
            df = processor.read(table_name=request.table_name)

        if df is None or df.empty:
            return DataResponse(
                columns=[],
                data=[],
                row_count=0,
                success=True
            )

        df = df.replace({np.nan: None})
        records = df.to_dict('records')

        logger.info(f"Query returned {len(records)} rows from table '{request.table_name}'")
        return DataResponse(
            columns=list(df.columns),
            data=records,
            row_count=len(df),
            success=True
        )

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        processor.disconnect()


@router.post("/delete", response_model=DeleteResponse)
async def delete_record(request: DeleteRequest):
    """
    Delete record(s) from database.

    Args:
        request: DeleteRequest with table name and criteria

    Returns:
        DeleteResponse with success status
    """
    processor = DatabaseDataProcessor()

    try:
        if not processor.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")

        success = processor.delete(
            criteria=request.criteria,
            table_name=request.table_name
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete record")

        logger.info(f"Deleted record(s) from table '{request.table_name}'")
        return DeleteResponse(success=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete operation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        processor.disconnect()


@router.post("/read", response_model=ReadResponse)
async def read_records(request: ReadRequest):
    """
    Read record(s) from database.

    Args:
        request: ReadRequest with table name, criteria, columns, and limit

    Returns:
        ReadResponse with retrieved data
    """
    processor = DatabaseDataProcessor()

    try:
        if not processor.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")

        df = processor.read(
            criteria=request.criteria,
            table_name=request.table_name,
            columns=request.columns,
            limit=request.limit
        )

        if df is None:
            raise HTTPException(status_code=500, detail="Failed to read records")

        if df.empty:
            return ReadResponse(data=[], success=True)

        df = df.replace({np.nan: None})
        records = df.to_dict('records')

        logger.info(f"Read {len(records)} record(s) from table '{request.table_name}'")
        return ReadResponse(data=records, success=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Read operation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        processor.disconnect()


@router.post("/update", response_model=UpdateResponse)
async def update_record(request: UpdateRequest):
    """
    Update record(s) in database.

    Args:
        request: UpdateRequest with table name, data, and criteria

    Returns:
        UpdateResponse with success status
    """
    processor = DatabaseDataProcessor()

    try:
        if not processor.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")

        data_dict = dict(request.data)

        for key, value in data_dict.items():
            if value is None or (isinstance(value, float) and np.isnan(value)):
                data_dict[key] = None

        success = processor.update(
            data=data_dict,
            criteria=request.criteria,
            table_name=request.table_name
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update record")

        logger.info(f"Updated record(s) in table '{request.table_name}'")
        return UpdateResponse(success=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update operation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        processor.disconnect()