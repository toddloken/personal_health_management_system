"""
Data retrieval endpoints

Provides REST API endpoints for database queries and data retrieval.

Location: backend/api/routes/data.py
"""

from typing import Optional
import numpy as np

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.utils.database_processor import DatabaseDataProcessor
from backend.logger import logger

router = APIRouter(prefix="/api/data", tags=["data"])


class DateRangeRequest(BaseModel):
    end_date: Optional[str] = None
    start_date: Optional[str] = None
    table_name: str = "personal_data"


class DataResponse(BaseModel):
    columns: list[str]
    data: list[dict]
    row_count: int
    success: bool


@router.post("/query", response_model=DataResponse)
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

            # Replace NaN values with None for JSON serialization
        df = df.replace({np.nan: None})

        records = df.to_dict('records')

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