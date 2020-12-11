# Timewarrior Sync Client
This repository contains the Client of the Timewarrior Sync project.

## Setup (for development)
### Using a virtual environment
To avoid conflicts between packages, you can use a virtual environment.
Make sure you have `virtualenv` installed (first time only):

```bash
pip install virtualenv
```

Create a new virtual environment (first time only):
```bash
virtualenv venv
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
To install the projects dependencies run:
```bash
pip install -r requirements.txt
```

Now you should be good to go :)

## Running the client

Once you have all dependencies installed, the client can be started:

```bash
python -m timewsync
```
