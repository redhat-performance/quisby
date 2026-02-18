import os

from quisby.benchmarks.fio.fio import extract_fio_run_data, extract_csv_data, group_data
from quisby.benchmarks.fio.summary import create_summary_fio_run_data
from quisby.benchmarks.fio.graph import graph_fio_run_data
from quisby.benchmarks.fio.comparison import compare_fio_run_results
from quisby.benchmarks.version_util import get_version_info
from quisby import custom_logger


def extract_etcd_data(path, system_name, OS_RELEASE):
    """
    Extract etcd data with version awareness.

    Dispatches to fio's CSV extraction functions with version support.
    """
    results = []
    ls_dir = os.listdir(path)

    # Get version information from the first CSV file
    first_file = path + f"/{ls_dir[0]}/result_etcd.csv" if ls_dir else None
    csv_version = None
    if first_file and os.path.exists(first_file):
        version_info = get_version_info(first_file)
        csv_version = version_info['raw'] or '1.0'

        custom_logger.debug(
            f"Processing ETCD CSV version {version_info['raw']} "
            f"(normalized: {version_info['normalized']})"
        )

    for idx, folder in enumerate(ls_dir):
        with open(path + f"/{folder}/result_etcd.csv") as csv_file:
            csv_data = csv_file.readlines()
            csv_data[-1] = csv_data[-1].strip()

            # Pass csv_version only for the first folder
            if idx == 0:
                results += extract_csv_data(csv_data, csv_version)
            else:
                results += extract_csv_data(csv_data)

    return group_data(results, system_name, OS_RELEASE, csv_version)


def create_summary_etcd_data(results):
    return create_summary_fio_run_data(results)


def graph_etcd_data(spreadsheetId, test_name, action):
    return graph_fio_run_data(spreadsheetId, test_name, action)


def compare_etcd_results(spreadsheets, spreadsheetId, test_name):
    return compare_fio_run_results(spreadsheets, spreadsheetId, test_name)
