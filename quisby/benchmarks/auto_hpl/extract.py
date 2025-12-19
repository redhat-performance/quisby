import logging
from typing import List, Dict, Optional
from pathlib import Path
from quisby.benchmarks.linpack.extract import linpack_format_data
from quisby.benchmarks.version_util import get_version_info


logger = logging.getLogger(__name__)


def _extract_v1_format(
        path: str,
        system_name: str,
        version_info: Dict
) -> Optional[List[Dict[str, str]]]:
    """
    Extract Auto HPL benchmark data from v1.x CSV format.

    Args:
        path (str): Path to the CSV file
        system_name (str): Name of the system being analyzed
        version_info (Dict): Version information from CSV

    Returns:
        Optional[List[Dict[str, str]]]: Processed benchmark results or None

    Raises:
        FileNotFoundError: If the specified file does not exist
        PermissionError: If there are insufficient permissions to read the file
        ValueError: If the file format is incorrect
    """
    # Validate input path
    file_path = Path(path)

    # Check file existence and extension
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if file_path.suffix.lower() != '.csv':
        raise ValueError(f"Invalid file type. Expected .csv, got {file_path.suffix}")


    # Read file with proper error handling
    with open(file_path, 'r', encoding='utf-8') as file:
        file_data = file.readlines()

        if not file_data:
            raise ValueError("Empty File")

        # Check for minimum required data
        if len(file_data) < 2:
            logger.warning(f"Insufficient data in file: {path}")
            return None

        data_row = None
        data_index = 0
        header_row = []
        for index, data in enumerate(file_data):
            if "Gflops" in data:
                data_index = index
                header_row = data.strip("\n").split(":")

        if not header_row:
            raise KeyError("Missing 'Gflops' in data")

        if len(file_data) > data_index+1:
            data_row = file_data[data_index+1].strip().split(":")

        # Check if insufficient data
        if not data_row:
            return None

        # Validate data extraction
        if len(header_row) != len(data_row):
            raise ValueError("Mismatched header and data lengths")

        # Create dictionary from rows
        data_dict = dict(zip(header_row, data_row))

        # Process and format data
        results: List[Dict[str, str]] = []
        formatted_results = linpack_format_data(
            results=results,
            system_name=system_name,
            gflops=data_dict["Gflops"]
        )

        # Add version info to results
        if formatted_results:
            csv_version = version_info['raw'] or '1.0'
            for result in formatted_results:
                result['csv_version'] = csv_version

        return formatted_results if formatted_results else None


def extract_auto_hpl_data(
        path: str,
        system_name: str
) -> Optional[List[Dict[str, str]]]:
    """
    Extract Auto HPL benchmark data with version awareness.

    Dispatches to appropriate handler based on CSV version.
    Supports backward compatibility for older CSV formats.

    Args:
        path (str): Path to the CSV file
        system_name (str): Name of the system being analyzed

    Returns:
        Optional[List[Dict[str, str]]]: Processed benchmark results or None

    Raises:
        FileNotFoundError: If the specified file does not exist
        PermissionError: If there are insufficient permissions to read the file
        ValueError: If the file format is incorrect
    """
    # Get version information from CSV
    version_info = get_version_info(path)
    normalized_version = version_info['normalized']

    logger.debug(
        f"Processing Auto HPL CSV version {version_info['raw']} "
        f"(normalized: {normalized_version})"
    )

    # Dispatch to version-specific handler
    if normalized_version in ['1.0', '1.1']:
        return _extract_v1_format(path, system_name, version_info)
    else:
        # Future: Add elif for version '2.0', '3.0', etc.
        logger.warning(
            f"Unknown CSV version {normalized_version}, attempting v1.x format"
        )
        return _extract_v1_format(path, system_name, version_info)
