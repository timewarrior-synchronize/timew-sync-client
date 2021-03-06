# Timewarrior Synchronization Client

This repository contains the client of the Timewarrior Sync project.

## Installation

### Using PIP

To install `timewsync` in your current Python environment:

```
pip install .
```

### Using Nix

To install `timewsync` in your current Nix environment:

```
nix-env -f default.nix -i
```

## Usage

```
usage: timewsync [-h] [--version] [--data-dir DATA_DIR]

timewarrior synchronization client

optional arguments:
  -h, --help           show this help message and exit
  --version            Print version information
  --data-dir DATA_DIR  The path to the data directory
```

### Data directory

The data directory contains all information

## Development

### Using a virtual environment

To avoid conflicts between packages, you can use a virtual environment.
Make sure you have `virtualenv` installed (first time only):

```bash
pip install virtualenv
```

Create a new virtual environment (first time only):
```bash
virtualenv -p python3 venv
```

To activate your virtual environment run:
```bash
# For bash users (usually default)
source venv/bin/activate

# For fish users
source venv/bin/activate.fish
```

On NixOS, all of the above steps boil down to:

```bash
nix-shell
```

### Installing the projects dependencies

To install the project dependencies:

```bash
pip install -r requirements.txt
```

Now you should be good to go :)

### Running the client

Once you have all dependencies installed, the client can be started:

```bash
python -m timewsync
```
