# AI DETECTOR

## Description

**AI DETECTOR** is an application that detects the use of AI tools and blocks user input until the correct password is entered. This application is oriented toward academic settings, where the goal is to limit AI use for specific cases.

## AI Tools Detected

- ChatGPT: https://chatgpt.com/
- Copilot: https://copilot.microsoft.com/
- Claude: https://claude.ai/new
- DeepSeek: https://www.deepseek.com/
- Gemini: https://gemini.google.com/app

## Features

- Real-time monitoring of active applications and windows
- User interface for password-based unlocking
- Alert sound while blocking is active

## Dependencies

Make sure you have the following Python packages installed:
```bash
pip install pynput pywinauto configparser
```

## Installation and Usage

### Running in Python

1. Clone the repository or download the source code.

```bash
git clone
```

2. Make sure you have a `config.ini` file with the structure:

```ini
[Configuration]
password=1234
```

3. Run the script:

```bash
python script.py
```

### Windows Installer

If you prefer to install the application:

1. Download the installer from the [Releases](https://github.com/tu_usuario/tu_repositorio/releases) section.
2. Run the `IADetecter_Setup.exe` file and install the application.
3. Launch the application from the generated shortcut.

## Configuration

The `config.ini` file allows you to change the unlock password without modifying the source code.

## License

This project is under the MIT license. You can modify and distribute it freely.

## Author

**AndresTY** - [GitHub](https://github.com/AndresTY)

## Contributions

Contributions are welcome. If you want to improve this project, send a *pull request* or open an *issue*.