"""
Test script for PythonPHMS Data Processor

Tests data loading from multiple sources:
- PostgreSQL database
- Text files (CSV, TSV)
- Excel spreadsheets

Run from project root: python tests/scripts/test_data.py
"""

import sys
from pathlib import Path
from datetime import datetime
import tempfile
import csv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.logger import logger

try:
    import pandas as pd
except ImportError:
    pd = None
    print("Warning: pandas not installed, some type checks may fail")


class DataProcessorTests:
    """Test suite for data processor functionality."""

    def __init__(self):
        self.test_results_dir = Path(r"/tests/test_results")
        self.test_data_dir = Path(r"/tests/fixtures/data")
        self.results = []
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0

        # Ensure directories exist
        self.test_results_dir.mkdir(parents=True, exist_ok=True)
        self.test_data_dir.mkdir(parents=True, exist_ok=True)

    def add_result(self, test_name: str, passed: bool, message: str = ""):
        """Add test result to results list."""
        self.test_count += 1
        status = "[PASS]" if passed else "[FAIL]"

        if passed:
            self.passed_count += 1
        else:
            self.failed_count += 1

        result_line = f"{status} Test {self.test_count}: {test_name}"
        if message:
            result_line += f" - {message}"

        self.results.append(result_line)
        print(result_line)

    def create_sample_csv(self, filepath: Path, rows: int = 10):
        """Create a sample CSV file for testing."""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'name', 'age', 'city', 'score'])

                for i in range(1, rows + 1):
                    writer.writerow([
                        i,
                        f'Person_{i}',
                        20 + (i % 50),
                        f'City_{(i % 5) + 1}',
                        50 + (i % 50)
                    ])
            return True
        except Exception as e:
            logger.error(f"Failed to create sample CSV: {e}")
            return False

    def create_sample_tsv(self, filepath: Path, rows: int = 10):
        """Create a sample TSV file for testing."""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(['id', 'name', 'age', 'city', 'score'])

                for i in range(1, rows + 1):
                    writer.writerow([
                        i,
                        f'Person_{i}',
                        20 + (i % 50),
                        f'City_{(i % 5) + 1}',
                        50 + (i % 50)
                    ])
            return True
        except Exception as e:
            logger.error(f"Failed to create sample TSV: {e}")
            return False

    def create_sample_excel(self, filepath: Path, rows: int = 10):
        """Create a sample Excel file for testing."""
        try:
            import openpyxl
            from openpyxl import Workbook

            wb = Workbook()
            ws = wb.active
            ws.title = "Sample Data"

            # Headers
            ws.append(['id', 'name', 'age', 'city', 'score'])

            # Data rows
            for i in range(1, rows + 1):
                ws.append([
                    i,
                    f'Person_{i}',
                    20 + (i % 50),
                    f'City_{(i % 5) + 1}',
                    50 + (i % 50)
                ])

            wb.save(filepath)
            return True
        except ImportError:
            logger.warning("openpyxl not installed - cannot create Excel test file")
            return False
        except Exception as e:
            logger.error(f"Failed to create sample Excel: {e}")
            return False

    def setup_test_files(self):
        """Create all necessary test files (setup phase - not counted as tests)."""
        print("\n" + "=" * 60)
        print("Setting up test files...")
        print("=" * 60 + "\n")

        # CSV file
        csv_file = self.test_data_dir / "sample_data.csv"
        if self.create_sample_csv(csv_file):
            print(f"✓ Created CSV test file: {csv_file}")
        else:
            print(f"✗ Failed to create CSV test file")

        # TSV file
        tsv_file = self.test_data_dir / "sample_data.tsv"
        if self.create_sample_tsv(tsv_file):
            print(f"✓ Created TSV test file: {tsv_file}")
        else:
            print(f"✗ Failed to create TSV test file")

        # Excel file
        excel_file = self.test_data_dir / "sample_data.xlsx"
        if self.create_sample_excel(excel_file):
            print(f"✓ Created Excel test file: {excel_file}")
        else:
            print(f"✗ Failed to create Excel test file (openpyxl may not be installed)")

        print("\nSetup complete. Starting DataProcessor tests...\n")

    def test_csv_loader(self):
        """Test CSV file loading functionality."""
        print("\n" + "=" * 60)
        print("Testing CSV Data Loader...")
        print("=" * 60 + "\n")

        try:
            from backend.utils.data_processor import DataProcessor
            import pandas as pd

            csv_file = self.test_data_dir / "sample_data.csv"
            processor = DataProcessor()

            # Test 1: Load CSV file returns DataFrame
            data = processor.load_csv(csv_file)
            if isinstance(data, pd.DataFrame) and len(data) > 0:
                self.add_result("CSV file loading returns DataFrame", True, f"Loaded {len(data)} rows")
            else:
                self.add_result("CSV file loading returns DataFrame", False, "No data loaded or not DataFrame")

            # Test 2: Verify columns
            expected_columns = ['id', 'name', 'age', 'city', 'score']
            if data is not None and list(data.columns) == expected_columns:
                self.add_result("CSV column verification", True)
            else:
                self.add_result("CSV column verification", False, f"Expected {expected_columns}")

            # Test 3: Verify data types
            if isinstance(data, pd.DataFrame):
                has_numeric = data['id'].dtype in ['int64', 'int32']
                has_string = data['name'].dtype == 'object'
                if has_numeric and has_string:
                    self.add_result("CSV data type verification", True)
                else:
                    self.add_result("CSV data type verification", False)

            # Test 4: Verify DataFrame is not empty
            if isinstance(data, pd.DataFrame) and not data.empty:
                self.add_result("CSV DataFrame not empty", True, f"Shape: {data.shape}")
            else:
                self.add_result("CSV DataFrame not empty", False)

            # Test 5: Handle missing file returns None
            missing_file = self.test_data_dir / "nonexistent.csv"
            result = processor.load_csv(missing_file)
            if result is None:
                self.add_result("CSV missing file returns None", True)
            else:
                self.add_result("CSV missing file returns None", False)

        except ImportError:
            self.add_result("CSV loader import", False, "DataProcessor not implemented yet")
        except Exception as e:
            self.add_result("CSV loader exception handling", False, str(e))

    def test_tsv_loader(self):
        """Test TSV file loading functionality."""
        print("\n" + "=" * 60)
        print("Testing TSV Data Loader...")
        print("=" * 60 + "\n")

        try:
            from backend.utils.data_processor import DataProcessor
            import pandas as pd

            tsv_file = self.test_data_dir / "sample_data.tsv"
            processor = DataProcessor()

            # Test 1: Load TSV file returns DataFrame
            data = processor.load_tsv(tsv_file)
            if isinstance(data, pd.DataFrame) and len(data) > 0:
                self.add_result("TSV file loading returns DataFrame", True, f"Loaded {len(data)} rows")
            else:
                self.add_result("TSV file loading returns DataFrame", False, "No data loaded or not DataFrame")

            # Test 2: Verify delimiter handling
            expected_columns = ['id', 'name', 'age', 'city', 'score']
            if data is not None and list(data.columns) == expected_columns:
                self.add_result("TSV delimiter handling", True)
            else:
                self.add_result("TSV delimiter handling", False)

            # Test 3: Verify DataFrame is not empty
            if isinstance(data, pd.DataFrame) and not data.empty:
                self.add_result("TSV DataFrame not empty", True, f"Shape: {data.shape}")
            else:
                self.add_result("TSV DataFrame not empty", False)

            # Test 4: Handle missing file returns None
            missing_file = self.test_data_dir / "nonexistent.tsv"
            result = processor.load_tsv(missing_file)
            if result is None:
                self.add_result("TSV missing file returns None", True)
            else:
                self.add_result("TSV missing file returns None", False)

        except ImportError:
            self.add_result("TSV loader import", False, "DataProcessor not implemented yet")
        except Exception as e:
            self.add_result("TSV loader exception handling", False, str(e))

    def test_excel_loader(self):
        """Test Excel file loading functionality."""
        print("\n" + "=" * 60)
        print("Testing Excel Data Loader...")
        print("=" * 60 + "\n")

        try:
            from backend.utils.data_processor import DataProcessor
            import pandas as pd

            excel_file = self.test_data_dir / "sample_data.xlsx"
            processor = DataProcessor()

            # Test 1: Load Excel file returns DataFrame
            data = processor.load_excel(excel_file)
            if isinstance(data, pd.DataFrame) and len(data) > 0:
                self.add_result("Excel file loading returns DataFrame", True, f"Loaded {len(data)} rows")
            else:
                self.add_result("Excel file loading returns DataFrame", False, "No data loaded or not DataFrame")

            # Test 2: Verify columns
            expected_columns = ['id', 'name', 'age', 'city', 'score']
            if data is not None and list(data.columns) == expected_columns:
                self.add_result("Excel column verification", True)
            else:
                self.add_result("Excel column verification", False)

            # Test 3: Verify DataFrame is not empty
            if isinstance(data, pd.DataFrame) and not data.empty:
                self.add_result("Excel DataFrame not empty", True, f"Shape: {data.shape}")
            else:
                self.add_result("Excel DataFrame not empty", False)

            # Test 4: Load specific sheet by name returns DataFrame
            data_by_name = processor.load_excel(excel_file, sheet_name="Sample Data")
            if isinstance(data_by_name, pd.DataFrame) and len(data_by_name) > 0:
                self.add_result("Excel sheet name loading returns DataFrame", True)
            else:
                self.add_result("Excel sheet name loading returns DataFrame", False)

            # Test 5: Handle missing file returns None
            missing_file = self.test_data_dir / "nonexistent.xlsx"
            result = processor.load_excel(missing_file)
            if result is None:
                self.add_result("Excel missing file returns None", True)
            else:
                self.add_result("Excel missing file returns None", False)

        except ImportError:
            self.add_result("Excel loader import", False, "DataProcessor not implemented yet")
        except Exception as e:
            self.add_result("Excel loader exception handling", False, str(e))

    def test_database_loader(self):
        """Test PostgreSQL database loading functionality."""
        print("\n" + "=" * 60)
        print("Testing PostgreSQL Database Loader...")
        print("=" * 60 + "\n")

        try:
            from backend.utils.database_processor import DatabaseDataProcessor
            import pandas as pd

            db = DatabaseDataProcessor()

            # Test 1: Connection establishment with .env
            if db.connect():
                self.add_result("Database connection using .env", True)
            else:
                self.add_result("Database connection using .env", False, "Check .env file configuration")
                return  # Stop if can't connect

            # Test 2: Verify connection returns actual connection object
            if db.connection is not None:
                self.add_result("Database connection object exists", True)
            else:
                self.add_result("Database connection object exists", False)

            # Test 3: Execute simple query and verify DataFrame return
            query = "SELECT 1 as test_column"
            result = db.execute_query(query)
            if isinstance(result, pd.DataFrame) and len(result) == 1:
                self.add_result("Database simple query returns DataFrame", True)
            else:
                self.add_result("Database simple query returns DataFrame", False)

            # Test 4: Get list of tables
            tables = db.get_tables()
            if isinstance(tables, list):
                self.add_result("Database get_tables returns list", True, f"Found {len(tables)} tables")
            else:
                self.add_result("Database get_tables returns list", False)

            # Test 5: Check if personal_data table exists
            if tables and 'personal_data' in tables:
                self.add_result("personal_data table exists", True)
                has_personal_data = True
            else:
                self.add_result("personal_data table exists", False, "Table not found")
                has_personal_data = False

            # Test 6: Create personal_data table if it doesn't exist
            if db.create_personal_data_table():
                self.add_result("Create personal_data table", True)
            else:
                self.add_result("Create personal_data table", False)

            # Test 7: Verify table now exists
            tables_after = db.get_tables()
            if 'personal_data' in tables_after:
                self.add_result("personal_data table verified after creation", True)
                has_personal_data = True
            else:
                self.add_result("personal_data table verified after creation", False)

            # Test 8: Read from personal_data table (returns DataFrame)
            if has_personal_data:
                personal_data = db.read_personal_data(limit=5)
                if isinstance(personal_data, pd.DataFrame):
                    self.add_result("read_personal_data returns DataFrame", True, f"{len(personal_data)} rows")
                else:
                    self.add_result("read_personal_data returns DataFrame", False)

                # Test 9: Verify DataFrame structure
                if isinstance(personal_data, pd.DataFrame):
                    expected_columns = ['pdate', 'sleep_index', 'steps', 'heart_rate', 'raw_notes']
                    has_columns = all(col in personal_data.columns for col in expected_columns)
                    if has_columns or len(personal_data) == 0:  # Empty is OK
                        self.add_result("personal_data DataFrame has expected columns", True)
                    else:
                        self.add_result("personal_data DataFrame has expected columns", False)

            # Test 10: Insert test data into personal_data
            test_data = {
                'pdate': '2024-11-28',
                'sleep_index': '85',
                'sleep_debt': '0:30',
                'steps': '8500',
                'heart_rate': '72',
                'ud_t': 1,
                'ud_a': 0,
                'ud_mj': 0,
                'ud_sd': 0,
                'ud_narc': 0,
                'raw_notes': 'Test data from test script'
            }
            if db.insert_personal_data(test_data):
                self.add_result("Insert data into personal_data", True)
            else:
                self.add_result("Insert data into personal_data", False)

            # Test 11: Read inserted data and verify DataFrame
            inserted_data = db.read_personal_data(
                start_date='2024-11-28',
                end_date='2024-11-28'
            )
            if isinstance(inserted_data, pd.DataFrame) and len(inserted_data) > 0:
                self.add_result("Read inserted data returns DataFrame", True)
            else:
                self.add_result("Read inserted data returns DataFrame", False)

            # Test 12: Update data in personal_data
            if db.update_personal_data(
                    {'raw_notes': 'Updated by test script'},
                    date='2024-11-28'
            ):
                self.add_result("Update personal_data by date", True)
            else:
                self.add_result("Update personal_data by date", False)

            # Test 13: Verify update worked
            updated_data = db.read_personal_data(
                start_date='2024-11-28',
                end_date='2024-11-28'
            )
            if isinstance(updated_data, pd.DataFrame) and len(updated_data) > 0:
                if updated_data.iloc[0]['raw_notes'] == 'Updated by test script':
                    self.add_result("Verify data update successful", True)
                else:
                    self.add_result("Verify data update successful", False)
            else:
                self.add_result("Verify data update successful", False)

            # Test 14: Generic read method returns DataFrame
            generic_data = db.read(table_name='personal_data', limit=5)
            if isinstance(generic_data, pd.DataFrame):
                self.add_result("Generic read returns DataFrame", True)
            else:
                self.add_result("Generic read returns DataFrame", False)

            # Test 15: Delete test data
            if db.delete_personal_data(date='2024-11-28'):
                self.add_result("Delete test data from personal_data", True)
            else:
                self.add_result("Delete test data from personal_data", False)

            # Test 16: Handle invalid query gracefully
            invalid_result = db.execute_query("SELECT * FROM nonexistent_table_xyz")
            if invalid_result is None:
                self.add_result("Database invalid query returns None", True)
            else:
                self.add_result("Database invalid query returns None", False)

            # Test 17: Legacy compatibility - load_table
            try:
                from backend.utils.data_processor import DataProcessor
                processor = DataProcessor()
                processor.connect_database()
                table_data = processor.load_table("personal_data")
                if isinstance(table_data, pd.DataFrame):
                    self.add_result("Legacy load_table returns DataFrame", True)
                else:
                    self.add_result("Legacy load_table returns DataFrame", False)
                processor.close_database()
            except Exception as e:
                self.add_result("Legacy load_table compatibility", False, str(e))

            # Test 18: Close connection
            if db.disconnect():
                self.add_result("Database disconnect", True)
            else:
                self.add_result("Database disconnect", False)

        except ImportError as e:
            self.add_result("Database loader import", False, f"Import error: {str(e)}")
        except Exception as e:
            self.add_result("Database loader exception handling", False, str(e))

    def test_unified_loader(self):
        """Test unified data loading interface."""
        print("\n" + "=" * 60)
        print("Testing Unified Data Loader Interface...")
        print("=" * 60 + "\n")

        try:
            from backend.utils.data_processor import DataProcessor

            processor = DataProcessor()

            # Test 1: Load from CSV using unified interface
            csv_file = self.test_data_dir / "sample_data.csv"
            data = processor.load_data(csv_file, source_type='csv')
            if data is not None and len(data) > 0:
                self.add_result("Unified CSV loading", True)
            else:
                self.add_result("Unified CSV loading", False)

            # Test 2: Load from Excel using unified interface
            excel_file = self.test_data_dir / "sample_data.xlsx"
            data = processor.load_data(excel_file, source_type='excel')
            if data is not None and len(data) > 0:
                self.add_result("Unified Excel loading", True)
            else:
                self.add_result("Unified Excel loading", False)

            # Test 3: Auto-detect file type
            data = processor.load_data(csv_file)
            if data is not None and len(data) > 0:
                self.add_result("Unified auto-detection", True)
            else:
                self.add_result("Unified auto-detection", False)

            # Test 4: Handle unsupported file type
            unsupported_file = self.test_data_dir / "sample_data.txt"
            result = processor.load_data(unsupported_file, source_type='unsupported')
            if result is None:
                self.add_result("Unified unsupported type handling", True)
            else:
                self.add_result("Unified unsupported type handling", False)

        except ImportError:
            self.add_result("Unified loader import", False, "DataProcessor not implemented yet")
        except Exception as e:
            self.add_result("Unified loader exception handling", False, str(e))

    def generate_report(self):
        """Generate test report and save to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = self.test_results_dir / f"data_processor_test_{timestamp}.txt"

        report = [
            "=" * 60,
            "PythonPHMS Data Processor Test Results",
            f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            f"Total Tests: {self.test_count}",
            f"Passed: {self.passed_count}",
            f"Failed: {self.failed_count}",
            f"Success Rate: {(self.passed_count / self.test_count * 100) if self.test_count > 0 else 0:.1f}%",
            "",
            "=" * 60,
            "Test Details",
            "=" * 60,
            ""
        ]

        report.extend(self.results)

        report.extend([
            "",
            "=" * 60,
            "Test Completion Summary",
            "=" * 60,
            "",
            "Test data files location:",
            f"  {self.test_data_dir}",
            "",
            "Test results saved to:",
            f"  {result_file}",
            "",
            "Next Steps:",
            "  1. Review test results above",
            "  2. Implement DataProcessor class in backend/utils/data_processor.py",
            "  3. Re-run tests to verify implementation",
            ""
        ])

        # Write to file
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        # Print summary
        print("\n" + "=" * 60)
        print(f"Test Summary: {self.passed_count}/{self.test_count} tests passed")
        print("=" * 60)
        print()
        print("Test data files location:")
        print(f"  {self.test_data_dir}")
        print()
        print("Test results saved to:")
        print(f"  {result_file}")
        print()

        return result_file


def run_all_tests():
    """Execute all data processor tests."""
    print("=" * 60)
    print("PythonPHMS Data Processor Test Suite")
    print("=" * 60)

    test_suite = DataProcessorTests()

    # Setup
    test_suite.setup_test_files()

    # Run all test groups
    # test_suite.test_csv_loader()
    # test_suite.test_tsv_loader()
    # test_suite.test_excel_loader()
    test_suite.test_database_loader()
    # test_suite.test_unified_loader()

    # Generate report
    test_suite.generate_report()


if __name__ == "__main__":
    run_all_tests()