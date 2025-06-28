# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python automation project for Wizard101 combat using the wizwalker library. The project contains a single main script that implements an automated combat handler called `LostSoulDestroyer` which casts "thunder snake" spells on Lost Soul monsters.

## Dependencies

The project uses wizwalker, a Python library for Wizard101 automation:
- **Installation**: `pip install git+https://codeberg.org/notfaj/wizwalker@development`
- **Note**: The PyPI version (`pip install wizwalker`) is outdated and no longer maintained. Always use the Codeberg repository version.

## Development Environment

- **Python Version**: Python 3.12.3 (use `python3` command)
- **Virtual Environment**: Windows-style venv located at `.venv/`
- **Activation**: Use `.venv/Scripts/python.exe` for running scripts
- **Package Management**: Use `.venv/Scripts/python.exe -m pip` for installing packages

## Running the Application

```bash
# Run the main script
.venv/Scripts/python.exe main.py
```

**Note**: The application requires an active Wizard101 client to function. It will fail with "IndexError: list index out of range" if no clients are detected.

## Architecture

### Core Components

- **main.py**: Single entry point containing:
  - `LostSoulDestroyer` class: Extends `CombatHandler` from wizwalker
  - `main()` function: Sets up client connection and combat handling
  - Combat logic: Automatically casts "thunder snake" on the first monster (assumed to be Lost Soul)

### Key Classes

- `LostSoulDestroyer(CombatHandler)`: Main combat automation class
  - `handle_round()`: Core combat logic executed each round
  - Searches for "thunder snake" card in hand
  - Targets first monster in monster list
  - Handles card not found scenarios gracefully

## Development Workflow

1. Ensure Wizard101 client is running
2. Use virtual environment Python executable for all operations
3. The script runs continuously until combat ends or client disconnects
4. Monitor console output for debugging information

## Common Tasks

- **Install dependencies**: `.venv/Scripts/python.exe -m pip install git+https://codeberg.org/notfaj/wizwalker@development`
- **Run script**: `.venv/Scripts/python.exe main.py`
- **Update wizwalker**: Re-run the pip install command above