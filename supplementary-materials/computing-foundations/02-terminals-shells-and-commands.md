# Terminals, shells, and commands

A **terminal** is the window or application where text commands are entered. A
**shell** is the program inside that terminal that interprets those commands.
Common shells include zsh and bash on macOS or Linux, and PowerShell on Windows.

The prompt might look like this:

```text
student@computer course-repository %
```

Type only the command after the prompt. Do not copy the prompt symbol itself.

## Four essential actions

| Goal | macOS/Linux | PowerShell |
| --- | --- | --- |
| Show current directory | `pwd` | `Get-Location` or `pwd` |
| List files | `ls` | `Get-ChildItem` or `ls` |
| Enter a folder | `cd folder-name` | `cd folder-name` |
| Move to parent folder | `cd ..` | `cd ..` |

Commands and paths are separated by spaces. If a path contains spaces, surround
it with quotes:

```text
cd "Data Science Course"
```

## Options and arguments

Consider:

```text
uv run pytest tests
```

- `uv` is the command;
- `run` tells `uv` what operation to perform;
- `pytest` is the program run inside the project environment;
- `tests` is an argument passed to `pytest`.

Many commands explain themselves with `--help`:

```text
uv --help
uv run pytest --help
```

## Stopping and history

- Press the Up Arrow to recall an earlier command.
- Press `Ctrl+C` to interrupt a running command.
- Closing the terminal ends its shell, but does not delete project files.
- Read error messages from the first line that identifies the failure; the last
  few lines often contain the most specific explanation.

## A safe practice sequence

From the repository root, run:

```text
pwd
ls
uv --version
uv run python --version
```

On PowerShell, `pwd` and `ls` work as convenient aliases. Your exact output will
differ, but it should identify the repository and Python 3.12.

## Safety

Do not paste an unfamiliar command simply because it appears online. First
identify the program, options, paths, and whether it installs, overwrites, or
deletes anything. Ask when uncertain.
