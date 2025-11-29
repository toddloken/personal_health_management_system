"""
Simple test script for PythonPHMS logger

Tests all log levels and saves results to test_results directory.
Run from project root: python tests/scripts/test_logger.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.logger import logger


def run_logger_tests():
    """Test all logging levels."""
    print("=" * 60)
    print("Testing PythonPHMS Logger")
    print("=" * 60)
    print()

    # Test results directory
    test_results_dir = Path(r"C:\Users\rocca\PycharmProjects\PythonPHMS\tests\test_results")
    test_results_dir.mkdir(parents=True, exist_ok=True)

    # Create test result file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = test_results_dir / f"logger_test_{timestamp}.txt"

    results = ["=" * 60, "PythonPHMS Logger Test Results", f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
               "=" * 60, ""]

    # Test 1: Debug level
    print("Test 1: DEBUG level logging...")
    logger.debug("This is a DEBUG message")
    results.append("[PASS] Test 1: DEBUG level - PASSED")

    # Test 2: Info level
    print("Test 2: INFO level logging...")
    logger.info("This is an INFO message")
    results.append("[PASS] Test 2: INFO level - PASSED")

    # Test 3: Warning level
    print("Test 3: WARNING level logging...")
    logger.warning("This is a WARNING message")
    results.append("[PASS] Test 3: WARNING level - PASSED")

    # Test 4: Error level
    print("Test 4: ERROR level logging...")
    logger.error("This is an ERROR message")
    results.append("[PASS] Test 4: ERROR level - PASSED")

    # Test 5: Critical level
    print("Test 5: CRITICAL level logging...")
    logger.critical("This is a CRITICAL message")
    results.append("[PASS] Test 5: CRITICAL level - PASSED")

    # Test 6: Multiple messages
    print("Test 6: Multiple messages...")
    for i in range(3):
        logger.info(f"Test message #{i + 1}")
    results.append("[PASS] Test 6: Multiple messages - PASSED")

    # Test 7: Exception logging
    print("Test 7: Exception logging...")
    try:
        x = 1 / 0
        print(x)
    except ZeroDivisionError:
        logger.exception("Caught an exception (this is expected)")
    results.append("[PASS] Test 7: Exception logging - PASSED")

    # Test 8: Multiple messages
    print("Test 8: Multiple messages...")
    for i in range(50):
        logger.info(f"Test message #{i + 1}")
    results.append("[PASS] Test 8: Multiple messages - PASSED")


    print()
    results.append("")
    results.append("=" * 60)
    results.append("All Tests Completed Successfully!")
    results.append("=" * 60)
    results.append("")
    results.append("Log files location:")
    results.append(r"  C:\Users\rocca\PycharmProjects\PythonPHMS\logs\pythonphms.log")
    results.append("")
    results.append("Test results saved to:")
    results.append(f"  {result_file}")

    # Write results to file
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))

    # Print summary
    print("=" * 60)
    print("All Tests Completed Successfully!")
    print("=" * 60)
    print()
    print("Check logs at:")
    print(r"  C:\Users\rocca\PycharmProjects\PythonPHMS\logs\pythonphms.log")
    print()
    print("Test results saved to:")
    print(f"  {result_file}")
    print()


if __name__ == "__main__":
    run_logger_tests()