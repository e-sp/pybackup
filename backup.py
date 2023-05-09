#!/usr/bin/env python3

import os
import subprocess
import shutil
from typing import Union
import yaml
import argparse
import time
from pprint import pprint as pp


archive_to_ratio = {
    "zip": 1.0,
    "tar": 1.0,
    "gztar": 0.5,
    "bztar": 0.5,
}

archive_to_file_extension = {
    "zip": "zip",
    "tar": "tar",
    "gztar": "tar.gz",
    "bztar": "tar.bz2",
}


def size_to_str(size: Union[int, float]) -> str:
    if size < 1024:
        return f"{size}B"
    elif size < 1024**2:
        return f"{size / 1024:.2f}KB"
    elif size < 1024**3:
        return f"{size / 1024 / 1024:.2f}MB"
    else:
        return f"{size / 1024 / 1024 / 1024:.2f}GB"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Backup files and directories to a specified location."
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Specify the config file to use. Defaults to config.yaml",
        default="config.yaml",
    )
    parser.add_argument(
        "--show-config",
        help="Show the config file and exit.",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--preview",
        help="Calculate the size of the backup and exit.",
        action="store_true",
    )
    parser.add_argument(
        "--size",
        help="Calculate the size of the backup and exit.",
        action="store_true",
    )
    args = parser.parse_args()
    return args


def execute_commands(commands: list[str]):
    for command in commands:
        process = subprocess.Popen(command, shell=True)
        process.wait()


def backup_location(
    location: str,
    archive_format: str,
    backup_dir: str,
    pre_backup_cmds: list[str],
    post_backup_cmds: list[str],
):
    print(f"Backing up {location}...")

    # Execute pre-backup commands
    print("Executing pre-backup commands...")
    execute_commands(pre_backup_cmds)

    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    if not archive_format in ["zip", "tar", "gztar", "bztar"]:
        print(f"Invalid archive format {archive_format}.")
        return

    archive_base_name = os.path.basename(location.rstrip(os.sep))

    # Create archive
    print(f"Creating {archive_format} archive...")
    shutil.make_archive(archive_base_name, archive_format, location)

    archive_source_name = f"{archive_base_name}.{archive_format}"
    archive_target_name = (
        f"{archive_base_name}.{archive_to_file_extension[archive_format]}"
    )

    # Remove existing archive if it exists
    target_path = os.path.join(backup_dir, archive_target_name)
    if os.path.exists(target_path):
        print(f"Removing existing archive from target path {target_path}...")
        os.remove(target_path)

    # Move archive to backup directory
    print(f"Moving {archive_source_name} archive to {backup_dir}...")
    shutil.move(archive_source_name, target_path)

    print("Executing post-backup commands...")
    execute_commands(post_backup_cmds)


def load_config(args: argparse.Namespace) -> dict:
    with open(args.config, "r") as config_file:
        config = yaml.safe_load(config_file)
    return config


def preview_backup(config: dict):
    total_size = 0
    for location in config["locations"]:
        location_size = 0
        ignored_files = 0
        for root, _, files in os.walk(location["path"]):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    location_size += file_size
                    total_size += file_size
                except FileNotFoundError:
                    ignored_files += 1
        print(
            f"Backup of {location['path']} will be "
            f"{size_to_str(location_size)} "
            f"({ignored_files} files ignored)"
        )
    print(f"Total backup size will be {size_to_str(total_size)}.")
    print(
        f"Expected archive size for {config['archive_format']} is "
        f"{size_to_str(total_size * archive_to_ratio[config['archive_format']])}"
    )


def backup_locations(config: dict):
    for location in config["locations"]:
        backup_location(
            location["path"],
            config["archive_format"],
            config["backup_directory"],
            location.get("pre_backup", []),
            location.get("post_backup", []),
        )


def backup_outputs(config: dict) -> bool:
    for output_config in config.get("outputs", []):
        if not "name" in output_config:
            print("No name specified for output.")
            return False

        if not "command" in output_config:
            print(f"No command specified for output {output_config['name']}.")
            return False

        print(f"Executing output {output_config['name']}...")
        backup_filename = os.path.join(
            config["backup_directory"],
            f"output-{output_config['name']}.txt",
        )
        with open(backup_filename, "wb") as f:
            f.write(subprocess.check_output(output_config["command"], shell=True))

    return True


def get_backup_size(config: dict) -> int:
    total_size = 0
    for root, _, files in os.walk(config["backup_directory"]):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.fsync(os.open(file_path, os.O_WRONLY))
                total_size += os.path.getsize(file_path)
            except FileNotFoundError:
                pass
    return total_size


def main():
    args = parse_args()
    config = load_config(args)

    # Show config and exit
    if args.show_config:
        pp(config)
        return

    # Preview backup
    if args.preview:
        preview_backup(config)
        return

    # Calculate backup size
    if args.size:
        print(f"Backup total size is {size_to_str(get_backup_size(config))}.")
        return

    # Backup each location
    start = time.time()
    backup_locations(config)
    backup_outputs(config)
    stop = time.time()

    # Print backup summary
    print(f"Backup completed in {stop - start:.2f} seconds.")
    print(f"Backup directory: {config['backup_directory']}")
    print(f"Backup total size is {size_to_str(get_backup_size(config))}.")


if __name__ == "__main__":
    main()
