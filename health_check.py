import configparser
import os
import re
import subprocess
import sys

from quisby import custom_logger


def check_predefined_folders():
    """Ensure required folders exist, otherwise create them."""
    home_dir = os.getenv("HOME")
    folders = [home_dir+'/.quisby/config/', home_dir+'/.quisby/logs/']

    # Loop through the folders to check if they exist
    for folder_path in folders:
        if not os.path.exists(folder_path):
            # Create folder if it doesn't exist
            os.makedirs(folder_path)
            custom_logger.info(f"Folder '{folder_path}' created.")
        else:
            # Log if the folder exists
            custom_logger.info(f"Folder '{folder_path}' already exists.")


def is_package_installed(package_name):
    """Check if a given package is installed via pip."""
    try:
        result = subprocess.run(['python3', '-m', 'pip', 'show', package_name], capture_output=True, text=True)
        # Return True if the package is installed, False otherwise
        return package_name in result.stdout
    except Exception as e:
        custom_logger.error(f"Error occurred while checking package {package_name}: {e}")
        return False


def check_and_install_requirements():
    """Install required packages from requirements.txt if not installed."""
    try:
        custom_logger.info("Checking if all the required packages are installed...")

        with open("requirements.txt", "r") as file:
            packages = file.read()

        # Extract package names and hashes using regular expressions
        package_info = re.findall(r"([a-zA-Z0-9_-]+)==[\d.]+(?:;\s+.*?)*(?:\s+--hash=([\w:]+))", packages)
        missing_packages = []

        # Check if each package is installed
        for package, _ in package_info:
            custom_logger.info(f"Checking for installation of package: {package}")
            if not is_package_installed(package):
                missing_packages.append(package)

        if missing_packages:
            custom_logger.error(f"The following packages are missing: {', '.join(missing_packages)}")
            custom_logger.info("Installing missing packages...")
            os.system("python3 -m pip install -r requirements.txt")
        else:
            custom_logger.info("All required packages are already installed.")
    except Exception as e:
        custom_logger.error(f"Failed to install required packages: {e}")
        sys.exit(1)


def create_virtual_environment(env_dir):
    """Create a Python virtual environment at the specified directory."""
    try:
        subprocess.check_call([sys.executable, '-m', 'venv', env_dir])
        custom_logger.info(f"Virtual environment created at {env_dir}")
    except subprocess.CalledProcessError:
        custom_logger.error("Failed to create virtual environment.")
        sys.exit(1)


def enter_virtual_environment(env_dir):
    """Activate the Python virtual environment."""
    activate_script = os.path.join(env_dir, 'bin', 'activate')
    if os.name == 'nt':
        activate_script = os.path.join(env_dir, 'Scripts', 'activate.bat')

    if os.path.exists(activate_script):
        try:
            subprocess.check_call([activate_script], shell=True)
            custom_logger.info("Successfully entered virtual environment.")
        except subprocess.CalledProcessError:
            custom_logger.error("Failed to activate virtual environment.")
            sys.exit(1)
    else:
        custom_logger.error("Error: Virtual environment activation script not found.")
        sys.exit(1)


def check_virtual_environment():
    """Check if the script is running inside a Python virtual environment."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        custom_logger.info("Running inside a virtual environment.")
        if sys.version_info < (3, 9):
            custom_logger.error(f"Python version inside the virtual environment is less than 3.9! Current version: {sys.version_info[0]}.{sys.version_info[1]}")
            sys.exit(1)
    else:
        custom_logger.warning("Not running inside a virtual environment.")
        custom_logger.warning("Create and activate a virtual environment with Python 3.9 or above.")
        sys.exit(1)


def check_python_version():
    """Ensure the Python version is 3.9 or higher."""
    if sys.version_info < (3, 9):
        custom_logger.error(f"Python 3.9 or higher is required to run this script. Current version: {sys.version_info[0]}.{sys.version_info[1]}")
        sys.exit(1)
    else:
        custom_logger.info(f"Python version {sys.version_info[0]}.{sys.version_info[1]} is installed.")


def validate_config_values(config, option):
    """Validate the values in the configuration file."""
    flag = 0  # A flag to track validation status

    # Validate paths for test and results
    if option == "process":
        test_path = config.get('test', 'test_path').strip()
        results_location = config.get('test', 'results_location').strip()

        if not (test_path and os.path.exists(test_path)):
            custom_logger.error(f"Test path '{test_path}' does not exist!")
            flag = 1
        if not (results_location and os.path.exists(results_location)):
            custom_logger.error(f"Results location '{results_location}' is invalid!")
            flag = 1

    # Validate system and cloud related configuration
    system_name = config.get('test', 'system_name').strip()

    if not system_name:
        custom_logger.warning("System name is not specified.")
        flag = 1

    os_type = config.get('test', 'OS_TYPE').strip()
    os_release = config.get('test', 'OS_RELEASE').strip()

    if not os_type:
        custom_logger.warning("OS type is not specified.")
    if not os_release:
        custom_logger.warning("OS release is not specified.")

    cloud_type = config.get('cloud', 'cloud_type').strip()
    region = config.get('cloud', 'region').strip()

    # Validate cloud_type
    valid_cloud_types = ['aws', 'gcp', 'azure', 'localhost']
    if cloud_type not in valid_cloud_types:
        custom_logger.error(f"Invalid cloud type '{cloud_type}'. Valid values are: {', '.join(valid_cloud_types)}.")
        flag = 1

    if cloud_type != "localhost":
        if not region:
            custom_logger.warning("OS release is not specified.")
            flag = 1
        custom_logger.warning("Ensure the region is correctly formatted for the chosen cloud provider.")

    # Check users field
    if config.has_option('access', 'users'):
        users = config.get('access', 'users').strip()
        if not users:
            custom_logger.warning("No users specified in the configuration.")

    # If there were validation errors, exit the script
    if flag:
        custom_logger.error("Configuration validation failed. Please fix the issues and try again.")
        sys.exit(1)


def check_for_config_fields(config_file, option):
    """Check if all required fields are present in the configuration file."""
    config = configparser.ConfigParser()
    try:
        # Read the configuration file
        config.read(config_file)

        # Define required fields for different sections
        required_fields = {
            'test': ['test_name', 'test_path', 'results_location', 'system_name', 'OS_TYPE', 'OS_RELEASE'],
            'spreadsheet': ['spreadsheet_id', 'spreadsheet_name', 'comp_id', 'comp_name'],
            'cloud': ['region', 'cloud_type'],
            'dependencies': ['specjbb_java_version'],
            'access': ['users'],
            'LOGGING': ['level', 'filename', 'max_bytes_log_file', 'backup_count']
        }

        # Check if all required fields exist
        for section, fields in required_fields.items():
            for field in fields:
                if not config.has_option(section, field):
                    custom_logger.error(f"Missing '{field}' field in section '{section}' of the configuration file!")
                    sys.exit(1)

        # Validate values for fields
        validate_config_values(config, option)

    except Exception as exc:
        custom_logger.error(f"Error reading configuration file: {exc}")
        sys.exit(1)


def check_config_file(config_file, option):
    """Check if the config file exists and validate its content."""
    custom_logger.info("Validating configuration file...")

    if not os.path.isfile(config_file):
        custom_logger.error(f"The provided config file '{config_file}' does not exist.")
        sys.exit(1)
    else:
        check_for_config_fields(config_file, option)


def health_check():
    """Perform an initial health check for the Quisby application."""
    custom_logger.info("**************************************** RUNNING QUISBY APPLICATION ****************************************")
    custom_logger.info("User documentation: https://docs.google.com/document/d/1g3kzp3pSMN_JVGFrFBWTXOeKaWG0jmA9x0QMAp299NI")
    custom_logger.info("Initial health check running...")

    # Run various checks
    check_predefined_folders()
    check_virtual_environment()
    check_python_version()
    check_and_install_requirements()


if __name__ == "__main__":
    # Start the health check process
    health_check()
