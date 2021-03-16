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
usage: timewsync [-h] [--version] [-v] [--data-dir DATA_DIR] {generate-key} ...

timewarrior synchronization client

positional arguments:
  {generate-key}
    generate-key       generates a new key pair.

optional arguments:
  -h, --help           show this help message and exit
  --version            print version information
  -v, --verbose        enable debug output
  --data-dir DATA_DIR  the path to the data directory
```

### Data directory

The data directory contains all information required by `timewsync`
for storing configuration options and tracking changes.

The path of the data directory defaults to `~/.timewsync`. This can be
overridden with the command line flag `--data-dir`.

#### Configuration

An example configuration file is available under `example.conf`. The
two available configuration options are the base URL of the server and
the client ID.

`timewsync` reads the configuration from `$TIMEWSYNC/timewsync.conf`
where `$TIMEWSYNC` represents the path of the data directory (i.e. if
the default data directory path is assumed, the configuration file is
at `~/.timewsync/timewsync.conf`).

#### Authentification keys

The public-private key pair used for authentification is also stored
in the data directory under `$TIMEWSYNC/private_key.pem` and
`$TIMEWSYNC/public_key.pem`. The key pair can be generated using the
`generate-keys` subcommand.

#### Hooks

Hooks are special files located in the data directory which will be
contextually executed on specific events. They reside in
`$TIMEWSYNC/hooks` (e.g. `$TIMEWSYNC/hooks/conflicts-occurred`).

Available hooks:

- `conflicts-occurred`: Triggered when the server responds with the
  information that a conflict has been resolved by merging intervals.

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

# Acknowledgements
This project was developed during the so-called "Bachelorpraktikum" at TU Darmstadt. It was supervised by the Department of Biology, [Computer-aided Synthetic Biology](https://www.bio.tu-darmstadt.de/forschung/ressearch_groups/Kabisch_Start.en.jsp). For more information visit [kabisch-lab.de](http://kabisch-lab.de).

This work was supported by the BMBF-funded de.NBI Cloud within the German Network for Bioinformatics Infrastructure (de.NBI) (031A532B, 031A533A, 031A533B, 031A534A, 031A535A, 031A537A, 031A537B, 031A537C, 031A537D, 031A538A).
