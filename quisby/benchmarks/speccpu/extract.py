import csv

from quisby import custom_logger

from quisby.util import read_config
from quisby.benchmarks.version_util import get_version_info


def _process_speccpu_v1(path, system_name, suite, OS_RELEASE, version_info):
    """Process SPECCPU data in v1.x format."""
    results = []

    with open(path) as csv_file:
        speccpu_results = list(csv.DictReader(csv_file, delimiter=":"))

    # Add version metadata
    csv_version = version_info['raw'] or '1.0'

    results.append([""])
    results.append([system_name, suite])
    results.append(["Benchmark", f"Base_Rate-{OS_RELEASE}", "CSV Version"])
    for idx, data_row in enumerate(speccpu_results):
        try:
            # Add csv_version only to the first data row
            if idx == 0:
                results.append([data_row['Benchmarks'], data_row['Base Rate'], csv_version])
            else:
                results.append([data_row['Benchmarks'], data_row['Base Rate']])
        except Exception as exc:
            custom_logger.debug(str(exc))
            pass
    return results


def extract_speccpu_data(path, system_name, OS_RELEASE):
    """
    Extract SPECCPU data with version awareness.

    Dispatches to appropriate handler based on CSV version.
    Supports backward compatibility for older CSV formats.
    """
    # Get version information from CSV
    version_info = get_version_info(path)
    normalized_version = version_info['normalized']

    custom_logger.debug(
        f"Processing SPECCPU CSV version {version_info['raw']} "
        f"(normalized: {normalized_version})"
    )

    results = []
    # Dispatch to version-specific handler
    if normalized_version in ['1.0', '1.1']:
        if "fprate" in path:
            fp_results = _process_speccpu_v1(path, system_name, "fprate", OS_RELEASE, version_info)
            results += fp_results
        elif "intrate" in path:
            int_results = _process_speccpu_v1(path, system_name, "intrate", OS_RELEASE, version_info)
            results += int_results
    else:
        # Future: Add elif for version '2.0', '3.0', etc.
        custom_logger.warning(
            f"Unknown CSV version {normalized_version}, attempting v1.x format"
        )
        if "fprate" in path:
            fp_results = _process_speccpu_v1(path, system_name, "fprate", OS_RELEASE, version_info)
            results += fp_results
        elif "intrate" in path:
            int_results = _process_speccpu_v1(path, system_name, "intrate", OS_RELEASE, version_info)
            results += int_results

    return results
