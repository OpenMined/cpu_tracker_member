import os
from pathlib import Path
import json
from syftbox.lib import Client, SyftPermission
import diffprivlib.tools as dp
import time
import psutil
from datetime import datetime, UTC


def get_cpu_usage_mean():
    """
    Calculate the mean CPU usage over a set of samples, using differential privacy for the final mean.

    The function collects CPU usage data using the `psutil` library over 50 samples taken at 0.1-second intervals. The mean of these
    samples is then calculated with differential privacy applied using `diffprivlib`. The output mean value is rounded to 2 decimal places.

    Returns:
        float: The differentially private mean CPU usage.
    """
    cpu_usage_values = []

    # Collect 50 CPU usage samples with a 0.1-second interval between each sample
    while len(cpu_usage_values) < 50:
        cpu_usage = psutil.cpu_percent()
        cpu_usage_values.append(cpu_usage)
        time.sleep(0.1)

    # Calculate the differentially private mean of the collected CPU usage values
    return round(
        dp.mean(
            cpu_usage_values,
            epsilon=0.5,  # Privacy parameter controlling the level of differential privacy
            bounds=(0, 100),  # Assumed bounds for CPU usage percentage (0-100%)
        ),
        2,  # Round to 2 decimal places
    )


def create_output_folder(path: Path) -> Path:
    """
    Create an output folder for CPU tracker data within the specified path.

    This function creates a directory structure for storing CPU tracker data under `app_pipelines/cpu_tracker`. If the directory
    already exists, it will not be recreated. Additionally, default permissions for accessing the created folder are set using the
    `SyftPermission` mechanism to allow the data to be read by an aggregator.

    Args:
        path (Path): The base path where the output folder should be created.

    """
    cpu_tracker_path: Path = path / "app_pipelines" / "cpu_tracker"
    os.makedirs(cpu_tracker_path, exist_ok=True)

    # Set default permissions for the created folder
    permissions = SyftPermission.datasite_default(email=client.email)
    permissions.read.append("aggregator@openmined.org")
    permissions.save(cpu_tracker_path)

    return cpu_tracker_path


def save(path: str, cpu_usage: float):
    """
    Saves CPU usage statistics to a JSON file.

    This function captures the average CPU usage along with a timestamp and saves this information
    into a specified JSON file.

    Args:
        path (str): The path where the JSON file will be saved.

    The JSON file will contain the following fields:
        - "cpu": The mean CPU usage percentage retrieved from `get_cpu_usage_mean()`.
        - "timestamp": A timestamp string (`timestamp_str`) indicating when the data was recorded.

    Example:
        >>> save("cpu_usage_data.json")
        # The specified file, "cpu_usage_data.json", will contain:
        # {
        #     "cpu": 45.6,
        #     "timestamp": "2024-11-12T10:30:00"
        # }

    Notes:
        - The function uses the `json` module to write the data in a human-readable format.
        - Make sure `get_cpu_usage_mean()` and `timestamp_str` are properly defined in the module.

    Raises:
        - IOError: If the file cannot be opened or written to.
    """
    current_time = datetime.now(UTC)
    timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "w") as json_file:
        json.dump(
            {"cpu": get_cpu_usage_mean(), "timestamp": timestamp_str},
            json_file,
            indent=4,
        )


if __name__ == "__main__":
    client = Client.load()
    
    # Create an output file with proper read permissions
    output_folder = create_output_folder(client.datasite_path)
    
    # Get cpu usage mean with differential privacy in it.
    cpu_usage = get_cpu_usage_mean()

    # Saving current cpu usage
    output_file: Path = output_folder / "cpu_tracker.json"
    save(path=str(output_file), cpu_usage=cpu_usage)
