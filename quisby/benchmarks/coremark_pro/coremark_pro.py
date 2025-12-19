import math
import re
from quisby import custom_logger
from quisby.pricing.cloud_pricing import get_cloud_pricing
from quisby.util import read_config
from quisby.benchmarks.version_util import get_version_info

def extract_prefix_and_number(input_string):
    """
    Extract the prefix, number, and suffix from an instance name.

    :param input_string: Instance name like 't2.micro-01'
    :return: Tuple (prefix, number, suffix) or (None, None, None) if no match.
    """
    match = re.search(r'^(.*?)(\d+)(.*?)$', input_string)
    if match:
        prefix = match.group(1)
        number = int(match.group(2))
        suffix = match.group(3)
        return prefix, number, suffix
    return None, None, None


def custom_key(item):
    """
    Generate a custom key for sorting or grouping instances based on cloud provider and instance name format.

    :param item: A tuple containing instance data.
    :return: A tuple key for grouping.
    """
    cloud_type = read_config("cloud", "cloud_type")
    try:
        if item[1][0] == "local":
            return item[1][0]
        elif cloud_type == "aws":
            instance_type, instance_number = item[1][0].split(".")
            return instance_type, instance_number
        elif cloud_type == "gcp":
            instance_type, instance_number = item[1][0].split("-")
            return instance_type, int(instance_number)
        elif cloud_type == "azure":
            instance_type, version, instance_number = extract_prefix_and_number(item[1][0])
            return instance_type, version, instance_number
    except Exception as exc:
        custom_logger.error(f"Error in custom_key for {item[1][0]}: {str(exc)}")
        return "", ""


def _extract_v1_format(path, system_name, OS_RELEASE, version_info):
    """
    Extract CoreMark-Pro data in v1.x CSV format.

    Format: colon-delimited CSV with # commented metadata
    """
    try:
        if not path.endswith(".csv"):
            return None
        with open(path) as file:
            lines = file.readlines()
    except Exception as exc:
        custom_logger.error(f"Unable to open or read file for CoreMark Pro: {path}")
        return None

    header, data_rows = [], []
    for line in lines:
        if line.strip().startswith('#') or not line.strip(): continue
        if not header:
            header = [h.strip() for h in line.strip().split(':')]
        else:
            data_rows.append([d.strip() for d in line.strip().split(':')])

    if not header or not data_rows: return None

    # Include version info in results
    csv_version = version_info['raw'] or '1.0'
    processed_results = [
        ['System', system_name, OS_RELEASE],
        ['CSV_Version', csv_version],
        header
    ] + data_rows
    return [processed_results]


def extract_coremark_pro_data(path, system_name, OS_RELEASE):
    """
    Extract CoreMark-Pro data with version awareness.

    Dispatches to appropriate handler based on CSV version.
    Supports backward compatibility for older CSV formats.
    """
    # Get version information from CSV
    version_info = get_version_info(path)
    normalized_version = version_info['normalized']

    custom_logger.debug(
        f"Processing CoreMark-Pro CSV version {version_info['raw']} "
        f"(normalized: {normalized_version})"
    )

    # Dispatch to version-specific handler
    if normalized_version in ['1.0', '1.1']:
        return _extract_v1_format(path, system_name, OS_RELEASE, version_info)
    else:
        # Future: Add elif for version '2.0', '3.0', etc.
        custom_logger.warning(
            f"Unknown CSV version {normalized_version}, attempting v1.x format"
        )
        return _extract_v1_format(path, system_name, OS_RELEASE, version_info)

def calc_price_performance(inst, avg):
    """
    Calculate price-perf ratio for an instance based on its cost per hour and performance.

    :param inst: Instance type or ID.
    :param avg: Average score for the instance.
    :return: Tuple (cost_per_hour, price_perf)
    """
    region = read_config("cloud", "region")
    cloud_type = read_config("cloud", "cloud_type")
    os_type = read_config("test", "os_type")
    cost_per_hour = None
    price_perf = 0.0
    try:
        cost_per_hour = get_cloud_pricing(inst, region, cloud_type.lower(), os_type)
        price_perf = float(avg) / float(cost_per_hour) if cost_per_hour else 0
    except Exception as exc:
        custom_logger.debug(str(exc))
        custom_logger.error("Error calculating price-performance!")
    return cost_per_hour, price_perf

def create_summary_coremark_pro_data(results, OS_RELEASE):
    """
    Creates a combined summary with both high-level totals AND detailed sub-test scores.
    Includes CSV version tracking for backward compatibility.
    """
    final_sheet_data = []

    for result_set in results:
        if not result_set: continue

        system_name = result_set[0][1]
        csv_version = result_set[1][1] if len(result_set) > 1 and result_set[1][0] == 'CSV_Version' else '1.0'

        # Data rows start after System and CSV_Version metadata
        header_idx = 2 if csv_version else 1
        data_rows = result_set[header_idx + 1:]
        
        # --- Part 1: Get High-Level Total Scores ---
        total_multi_score, total_single_score = 0.0, 0.0
        for row in data_rows:
            if row[0].lower() == 'score':
                total_multi_score = float(row[1])
                total_single_score = float(row[2])
                break
        
        cph, single_pps = calc_price_performance(system_name, total_single_score)
        _, multi_pps = calc_price_performance(system_name, total_multi_score)

        # --- Part 2: Get Detailed Sub-test Scores ---
        single_iter_details = []
        multi_iter_details = []
        for row in data_rows:
            if row[0].lower() == 'score': continue
            single_iter_details.append([row[0], float(row[2])])
            multi_iter_details.append([row[0], float(row[1])])

        # --- Part 3: Assemble All Tables for the Sheet ---
        # High-Level Summary Tables (include CSV version in first table only for tracking)
        final_sheet_data.extend([["Single Iterations"], ["System name", f"Score-{OS_RELEASE}", "CSV Version"], [system_name, total_single_score, csv_version], [""]])
        final_sheet_data.extend([["Multi Iterations"], ["System name", f"Score-{OS_RELEASE}"], [system_name, total_multi_score], [""]])
        final_sheet_data.extend([["Cost/Hr"], ["System name", "Cost/Hr"], [system_name, cph], [""]])
        final_sheet_data.extend([["Single Iterations Price-perf"], ["System name", f"Score/$-{OS_RELEASE}"], [system_name, single_pps], [""]])
        final_sheet_data.extend([["Multi Iterations Price-perf"], ["System name", f"Score/$-{OS_RELEASE}"], [system_name, multi_pps], [""]])
        
        # Detailed Sub-test Tables
        final_sheet_data.extend([["Single Iterations Details"], ["Test", f"Score-{OS_RELEASE}"]] + single_iter_details)
        final_sheet_data.append([""])
        final_sheet_data.extend([["Multi Iterations Details"], ["Test", f"Score-{OS_RELEASE}"]] + multi_iter_details)
        final_sheet_data.append([""])

    return final_sheet_data
