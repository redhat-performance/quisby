"""
CSV Version Utilities for Quisby

Provides version parsing and management for benchmark CSV files.
Ensures backward compatibility when CSV formats change.

Usage Example:
    from quisby.benchmarks.version_util import (
        get_version_info,
        version_dispatch
    )

    def extract_benchmark_data(path, system_name, OS_RELEASE):
        # Dispatch based on version
        version_info = get_version_info(path)

        if version_info['normalized'] in ['1.0', '1.1']:
            return _extract_v1_format(path, system_name, OS_RELEASE, version_info)
        elif version_info['normalized'] == '2.0':
            return _extract_v2_format(path, system_name, OS_RELEASE, version_info)
        else:
            raise ValueError(f"Unsupported version: {version_info['raw']}")

    # Or use the helper:
    def extract_benchmark_data(path, system_name, OS_RELEASE):
        return version_dispatch(
            path,
            handlers={
                '1.0': _extract_v1_format,
                '1.1': _extract_v1_format,  # v1.1 compatible with v1.0
                '2.0': _extract_v2_format,
            },
            args=(system_name, OS_RELEASE)
        )
"""

import re
from quisby import custom_logger


def parse_csv_version(file_path):
    """
    Parse the CSV version from the file metadata.

    Looks for '# Results version: <version>' in the CSV file header.

    :param file_path: Path to the CSV file
    :return: Version string (e.g., 'v1.1.2743', '1.0') or None if not found
    """
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()

                # Stop searching after metadata section
                if line == '# Test general meta end':
                    break

                # Look for version line
                if line.startswith('# Results version:'):
                    version = line.split(':', 1)[1].strip()
                    return version

        # No version found - assume legacy format
        custom_logger.debug(f"No version found in {file_path}, assuming v1.0")
        return None

    except Exception as exc:
        custom_logger.error(f"Error parsing version from {file_path}: {exc}")
        return None


def parse_csv_metadata(file_path):
    """
    Parse all metadata from CSV file header.

    Returns a dictionary with all metadata fields from the CSV header.

    :param file_path: Path to the CSV file
    :return: Dictionary of metadata key-value pairs
    """
    metadata = {}

    try:
        with open(file_path, 'r') as file:
            in_metadata = False

            for line in file:
                line = line.strip()

                # Track metadata sections
                if line == '# Test general meta start':
                    in_metadata = True
                    continue
                elif line == '# Test general meta end':
                    break

                # Parse metadata lines
                if in_metadata and line.startswith('#'):
                    # Remove leading '#' and split on first ':'
                    content = line[1:].strip()
                    if ':' in content:
                        key, value = content.split(':', 1)
                        metadata[key.strip()] = value.strip()

        return metadata

    except Exception as exc:
        custom_logger.error(f"Error parsing metadata from {file_path}: {exc}")
        return {}


def normalize_version(version_string):
    """
    Normalize version string to comparable format.

    Examples:
        'v1.1.2743' -> '1.1'
        '2.0.1' -> '2.0'
        None -> '1.0'

    :param version_string: Raw version string from CSV
    :return: Normalized version string (major.minor)
    """
    if not version_string:
        return '1.0'

    # Remove 'v' prefix if present
    version_string = version_string.lstrip('vV')

    # Extract major.minor version
    match = re.match(r'^(\d+)\.(\d+)', version_string)
    if match:
        return f"{match.group(1)}.{match.group(2)}"

    # Fallback
    return '1.0'


def get_version_info(file_path):
    """
    Get comprehensive version information from CSV file.

    :param file_path: Path to the CSV file
    :return: Dictionary with 'raw', 'normalized', and 'metadata' keys
    """
    raw_version = parse_csv_version(file_path)
    normalized = normalize_version(raw_version)
    metadata = parse_csv_metadata(file_path)

    return {
        'raw': raw_version,
        'normalized': normalized,
        'metadata': metadata
    }


def version_dispatch(path, handlers, args=(), kwargs=None, default_version='1.0'):
    """
    Dispatch CSV extraction to version-specific handler.

    This helper function parses the CSV version and calls the appropriate handler.

    :param path: Path to the CSV file
    :param handlers: Dictionary mapping version strings to handler functions
                     Example: {'1.0': extract_v1, '2.0': extract_v2}
    :param args: Positional arguments to pass to the handler
    :param kwargs: Keyword arguments to pass to the handler
    :param default_version: Version to use if CSV has no version (default: '1.0')
    :return: Result from the version-specific handler, with version info attached
    """
    if kwargs is None:
        kwargs = {}

    # Get version info
    version_info = get_version_info(path)
    normalized_version = version_info['normalized']
    raw_version = version_info['raw'] or default_version

    # Find appropriate handler
    if normalized_version in handlers:
        handler = handlers[normalized_version]
        custom_logger.debug(f"Using version {normalized_version} handler for {path}")
    elif default_version in handlers:
        handler = handlers[default_version]
        custom_logger.warning(
            f"No handler for version {normalized_version} ({raw_version}), "
            f"using default v{default_version} handler for {path}"
        )
    else:
        raise ValueError(
            f"Unsupported CSV version {normalized_version} ({raw_version}) "
            f"and no default handler available. Supported versions: {list(handlers.keys())}"
        )

    # Call the handler
    result = handler(path, *args, **kwargs)

    # Attach version info to result for downstream tracking
    if result is not None and isinstance(result, dict):
        result['csv_version'] = raw_version

    return result
