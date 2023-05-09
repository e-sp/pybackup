# backup.py

This project provides a Python script to backup files and directories to a specified location. The script supports various archive formats and allows for pre- and post-backup commands to be executed. The configuration is done through a YAML file, and an example configuration is provided.

## Features

- Backup files and directories to a specified location
- Supports various archive formats: zip, tar, gztar, bztar
- Execute pre- and post-backup commands
- Calculate the size of the backup
- Preview backup size before execution
- Backup outputs of specified commands

## Requirements

- Python 3.6 or higher
- PyYAML

## Installation

1. Clone the repository or download the `backup.py` script.
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Create a configuration file (e.g., `config.yaml`) based on the provided example.
2. Run the script with the desired options:

```bash
python backup.py -c config.yaml
```

### Command Line Options

- `-c, --config`: Specify the config file to use. Defaults to `config.yaml`.
- `--show-config`: Show the config file and exit.
- `-p, --preview`: Calculate the size of the backup and exit.
- `--size`: Calculate the size of the backup and exit.

## Example Configuration

An example configuration file (`config.yaml`) is provided in the repository. This file contains the backup directory, archive format, locations to backup, and pre- and post-backup commands.

## License

This project is licensed under the MIT License.
