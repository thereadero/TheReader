# FFmpeg Video Converter (proj2.py)

## Overview

This project is a simple graphical user interface (GUI) application for converting video files using FFmpeg. It is built with Python's Tkinter library and supports drag-and-drop functionality for easy file input. The app allows users to customize output resolution and video codec, making it suitable for basic video processing tasks.

## Features

- **Drag and Drop Support**: Users can drag video files directly onto the application window to set the input file.
- **File Browsing**: Browse buttons for selecting input and output files via standard file dialogs.
- **Customizable Resolution**: Dropdown menu with preset resolutions (original, 720p, 1080p, 4K) or custom input.
- **Video Codec Selection**: Dropdown menu with common codecs (libx264, libx265, vp9, libvpx-vp9, copy).
- **Automatic Output Suggestion**: When an input file is selected, the app suggests an output filename with "_converted.mp4".
- **Output Folder Access**: After successful conversion, the output folder automatically opens, allowing users to drag the file elsewhere.
- **Error Handling**: Displays messages for missing files, FFmpeg errors, or invalid inputs.

## Requirements

- **Python 3.x**: The application is written in Python.
- **FFmpeg**: Must be installed on the system and accessible via command line (add to PATH).
  - Download from: https://ffmpeg.org/download.html
- **Python Packages**:
  - `tkinter` (built-in with Python)
  - `tkinterdnd2` (install via `pip install tkinterdnd2`)

## Installation

1. Ensure Python 3.x is installed.
2. Install FFmpeg:
   - Download the appropriate version for your OS from the FFmpeg website.
   - Extract and add the `bin` folder to your system's PATH environment variable.
3. Install required Python packages:
   ```
   pip install tkinterdnd2
   ```
4. Clone or download the project files.
5. Run the application:
   ```
   python proj2.py
   ```

## Usage

1. **Launch the Application**:
   - Run `python proj2.py` from the command line in the project directory.

2. **Select Input File**:
   - Use the "Browse" button next to "Input File" to open a file dialog and select a video file.
   - Alternatively, drag and drop a video file onto the gray "Drag and drop video file here" area.

3. **Set Output File**:
   - The output file path is auto-suggested based on the input file (e.g., `input_converted.mp4`).
   - Use the "Browse" button to choose a different location and filename via a save dialog.

4. **Configure Options**:
   - **Resolution**: Select from presets or enter a custom resolution (e.g., "1920x1080"). "original" keeps the input resolution.
   - **Video Codec**: Choose from the dropdown (e.g., "libx264" for H.264 encoding).

5. **Convert**:
   - Click the "Convert" button.
   - The app will run FFmpeg with the specified settings.
   - On success, a message box confirms completion, and the output folder opens.

6. **Supported Formats**:
   - Input: Common video formats like MP4, AVI, MKV, MOV, WMV.
   - Output: Defaults to MP4, but can be changed in the save dialog.

## Code Structure

The application is contained in `proj2.py` and consists of a single class:

- **VideoConverter Class**:
  - Inherits from `TkinterDnD.Tk` for drag-and-drop support.
  - **__init__()**: Sets up the GUI elements, variables, and event bindings.
  - **browse_input()**: Opens a file dialog for input selection and suggests output.
  - **browse_output()**: Opens a save dialog for output selection.
  - **on_drop(event)**: Handles drag-and-drop events to set input file.
  - **convert()**: Builds and executes the FFmpeg command, handles errors, and opens output folder.

### FFmpeg Command Example

The app constructs commands like:
```
ffmpeg -i input.mp4 -vf scale=1920x1080 -c:v libx264 -c:a aac -y output.mp4
```
- `-i`: Input file
- `-vf scale=...`: Video filter for resolution (omitted if "original")
- `-c:v`: Video codec
- `-c:a aac`: Audio codec (fixed to AAC)
- `-y`: Overwrite output without prompting

## Troubleshooting

- **FFmpeg Not Found**: Ensure FFmpeg is installed and in PATH. Test with `ffmpeg -version` in command prompt.
- **Drag and Drop Not Working**: Ensure `tkinterdnd2` is installed correctly.
- **Conversion Errors**: Check input file validity and FFmpeg compatibility. View error messages for details.
- **No GUI on Some Systems**: Tkinter may require additional setup on Linux; ensure `python3-tk` is installed.

## Future Enhancements

- Add audio codec selection.
- Support for batch conversion.
- Progress bar during conversion.
- Preview window for output.
- Cross-platform testing (currently optimized for Windows).

## License

This project is for educational purposes. FFmpeg is licensed under LGPL/GPL.