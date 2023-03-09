# NJU Internet

Login, keep login or logout from Internet securely in NJU.

The script uses a portal API with the https protocol, which still works so far (2023.3).

The passwords are read directly from tty without echo, instead of command line arguments or python files, preventing the secure issues in other scripts.

- [Preparation](#preparation)
- [Usage](#usage)
  - [Login](#login)
  - [Logout](#logout)
  - [Keep login in the foreground (*NOT* recommended)](#keep-login-in-the-foreground-not-recommended)
  - [Keep login in the background (recommended)](#keep-login-in-the-background-recommended)
  - [Keep login for several hours in the background](#keep-login-for-several-hours-in-the-background)

## Preparation

Install requests.
```bash
python3 -m pip install requests
```

## Usage

### Login

```bash
python3 main.py login
```

### Logout

```bash
python3 main.py logout
```

### Keep login in the foreground (*NOT* recommended)

```bash
python3 main.py keep
```

### Keep login in the background (recommended)

```bash
python3 main.py keep --tstp; bg; disown
```

or simply

```bash
. ./keep
```

Please note the dots and the spaces above.

### Keep login for several hours in the background

```bash
python3 main.py keep --tstp --duration 24; bg; disown
```

or simply

```bash
. ./keep --duration 24
```

Please note the dots and the spaces above.

More optins can be found in the help message of the script.

After running `install.sh`, you can replace `python3 main.py` with `internet` in all of the commands.
