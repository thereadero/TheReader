# FFmpeg Video Converter (ffmpeg_conv.py)

## Overview

This project is a feature-rich graphical user interface (GUI) application for converting video files using FFmpeg. It is built with Python's Tkinter library and utilizes `tkinterdnd2` for drag-and-drop file imports. The application allows users to customize output resolution and video codecs, provides a real-time command-line preview, and automatically optimizes resolution choices based on the source video.

---

## Features

- **Drag and Drop Support**: Drag video files directly onto the gray "Drag and drop video file here" area to set the input file path.
- **File Browsing**: Browse buttons for selecting input and output files via standard system file dialogs.
- **Smart Resolution Selection**: 
  - Supports presets from 240p up to 8K (`426x240` to `7680x4320`).
  - **Upscaling Protection**: When an input file is loaded, the app runs `ffprobe` to determine the video's original dimensions and dynamically filters out any presets that would result in upscaling the video.
- **Format & Codec Configuration**: Dropdown menu mapping user-friendly container options to specific video encoders and extensions:
  - `MP4 (H.264)` -> `libx264` codec (`.mp4`)
  - `MP4 (H.265)` -> `libx265` codec (`.mp4`)
  - `AVI (MPEG4)` -> `mpeg4` codec (`.avi`)
  - `MKV (H.264)` -> `libx264` codec (`.mkv`)
  - `WebM (VP9)` -> `libvpx-vp9` codec (`.webm`)
  - `Original (Copy)` -> `copy` stream (`*` original file extension)
- **Automatic Extension Syncing**: Choosing a new codec automatically updates the output file's extension to prevent container conflicts.
- **Real-Time Shell Command Preview**: Displays the exact FFmpeg command that will run in the shell, updating instantly as the user modifies files, resolution, or format.
- **Progressive Clearing**: A "Clear" button resets all fields and restores resolution options.
- **Output Folder Auto-Open**: Automatically opens the output directory in File Explorer once the conversion successfully completes.

---

## Requirements

- **Python 3.x**
- **FFmpeg & FFprobe**: Must be installed on the system and accessible via the command line (added to PATH).
  - Download from: https://ffmpeg.org/download.html
- **Python Packages**:
  - `tkinter` (built-in with Python)
  - `tkinterdnd2` (install via `pip install tkinterdnd2`)

---

## Installation

1. Ensure Python 3.x is installed.
2. Install FFmpeg:
   - Download the appropriate version for your OS from the FFmpeg website.
   - Extract and add the `bin` folder (containing `ffmpeg.exe` and `ffprobe.exe`) to your system's PATH environment variable.
3. Install the required Python packages:
   ```bash
   pip install tkinterdnd2
   ```
4. Run the application:
   ```bash
   python ffmpeg_conv.py
   ```

---

## Usage

1. **Launch the Application**:
   - Run `python ffmpeg_conv.py` in the terminal inside the `ffmpeg_conv` directory.

2. **Select Input File**:
   - Use the "Browse" button next to "Input File".
   - Or drag and drop a video file onto the light gray area.

3. **Configure Options**:
   - **Resolution**: Select from the dynamically populated dropdown (highest resolutions are filtered out if they exceed the source dimensions). Selecting "original" keeps the input resolution.
   - **Format/Codec**: Choose the desired container format and encoder. The output filename extension will automatically adjust.

4. **Review Generated Command**:
   - Inspect the "Generated Command" text field to verify the FFmpeg parameters.

5. **Convert**:
   - Click the "Convert" button.
   - On success, the app clears the fields, displays a success pop-up, and opens the destination folder.

---

## Code Structure

The application is structured inside [ffmpeg_conv.py](file:///c:/Users/ondra/Documents/git_game/TheReader/ffmpeg_conv/ffmpeg_conv.py) and consists of the main controller class:

- **`VideoConverter`**:
  - Inherits from `TkinterDnD.Tk` for drag-and-drop window capabilities.
  - **`__init__()`**: Configures window size (`600x550`), setups string variables, initializes the UI grid/widgets, and sets up `trace_add` variable listeners to drive updates to the command preview.
  - **`on_format_change()`**: Automatically updates the output string path's file extension to match the container.
  - **`update_cmd_preview()`**: Generates and prints the formatted FFmpeg parameters in the preview text area.
  - **`browse_input()`**: Standard file picker window for input video formats (`*.mp4 *.avi *.mkv *.mov *.wmv`).
  - **`browse_output()`**: Standard save file picker window.
  - **`on_drop(event)`**: Cleans up drag-and-drop path strings and sets the target input.
  - **`get_video_resolution(file_path)`**: Launches `ffprobe` in a background subprocess to query width and height of the video file.
  - **`update_resolution_options(file_path)`**: Filters out upscale resolutions, preventing presets higher than the source file from being selected.
  - **`convert()`**: Spawns `ffmpeg` as a subprocess, displays messagebox errors/successes, and opens the output directory.
  - **`clear_fields()`**: Resets GUI elements to their default states.

---

## Troubleshooting

- **FFmpeg/FFprobe Not Found**: Check that `ffmpeg -version` and `ffprobe -version` run successfully in your command prompt. If not, verify they are added to PATH.
- **Drag and Drop Fails**: Check if `tkinterdnd2` is correctly installed on your current Python environment.
- **No GUI on Linux**: Ensure `python3-tk` is installed via your package manager.