import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import re
from tkinterdnd2 import TkinterDnD, DND_FILES

class VideoConverter(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("FFmpeg Video Converter")
        self.geometry("600x550")

        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.resolution = tk.StringVar(value="1920x1080")
        self.format_name = tk.StringVar(value="MP4 (H.264)")

        self.RESOLUTIONS = [
            "original", 
            "426x240", "640x360", "854x480", "1024x576", 
            "1280x720", "1920x1080", "2048x1080", "2560x1440", 
            "3840x2160", "4096x2160", "5120x2880", "6016x3384", "7680x4320"
        ]
        self.FORMAT_MAP = {
            "MP4 (H.264)": ("libx264", ".mp4"),
            "MP4 (H.265)": ("libx265", ".mp4"),
            "AVI (MPEG4)": ("mpeg4", ".avi"),
            "MKV (H.264)": ("libx264", ".mkv"),
            "WebM (VP9)": ("libvpx-vp9", ".webm"),
            "Original (Copy)": ("copy", "")
        }

        # UI Elements
        # Input File
        input_frame = tk.Frame(self)
        input_frame.pack(pady=5)
        tk.Label(input_frame, text="Input File:").pack(side=tk.LEFT)
        self.input_entry = tk.Entry(input_frame, textvariable=self.input_file, width=40)
        self.input_entry.pack(side=tk.LEFT)
        tk.Button(input_frame, text="Browse", command=self.browse_input).pack(side=tk.LEFT)

        # Drag and Drop Area
        self.drop_label = tk.Label(self, text="Drag and drop video file here", bg="lightgray", height=5, relief="sunken")
        self.drop_label.pack(fill=tk.X, padx=10, pady=10)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)

        # Output File
        output_frame = tk.Frame(self)
        output_frame.pack(pady=5)
        tk.Label(output_frame, text="Output File:").pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=self.output_file, width=40).pack(side=tk.LEFT)
        tk.Button(output_frame, text="Browse", command=self.browse_output).pack(side=tk.LEFT)

        tk.Label(self, text="Resolution:").pack(pady=5)
        self.resolution_combo = ttk.Combobox(self, textvariable=self.resolution,
                                             values=self.RESOLUTIONS)
        self.resolution_combo.pack(pady=5)

        # Format/Codec
        tk.Label(self, text="Format/Codec:").pack(pady=5)
        self.codec_combo = ttk.Combobox(self, textvariable=self.format_name,
                                        values=list(self.FORMAT_MAP.keys()))
        self.codec_combo.pack(pady=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Convert", command=self.convert).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear_fields).pack(side=tk.LEFT, padx=5)

        # Command Preview
        tk.Label(self, text="Generated Command:").pack(pady=(10, 0))
        self.cmd_preview = tk.Text(self, height=3, width=70, state=tk.DISABLED, bg="#f0f0f0")
        self.cmd_preview.pack(pady=5, padx=10)

        # Setup traces to update command preview
        self.input_file.trace_add("write", lambda *args: self.update_cmd_preview())
        self.output_file.trace_add("write", lambda *args: self.update_cmd_preview())
        self.resolution.trace_add("write", lambda *args: self.update_cmd_preview())
        self.format_name.trace_add("write", lambda *args: self.on_format_change())
        
        self.update_cmd_preview()

    def on_format_change(self):
        # Update extension if possible
        format_name = self.format_name.get()
        if format_name in self.FORMAT_MAP:
            _, ext = self.FORMAT_MAP[format_name]
            if ext:
                current_output = self.output_file.get()
                if current_output:
                    base, old_ext = os.path.splitext(current_output)
                    if old_ext != ext:
                        self.output_file.set(base + ext)
        
        self.update_cmd_preview()

    def update_cmd_preview(self):
        input_file = self.input_file.get() or "input_file.mp4"
        output_file = self.output_file.get() or "output_file.mp4"
        resolution = self.resolution.get()
        format_name = self.format_name.get()
        
        codec = self.FORMAT_MAP.get(format_name, ("libx264", ".mp4"))[0]

        cmd = ["ffmpeg", "-i", input_file]
        if resolution != "original":
            cmd.extend(["-vf", f"scale={resolution}"])
        cmd.extend(["-c:v", codec, "-c:a", "aac", "-y", output_file])

        cmd_str = " ".join(f'"{x}"' if " " in x else x for x in cmd)

        self.cmd_preview.config(state=tk.NORMAL)
        self.cmd_preview.delete("1.0", tk.END)
        self.cmd_preview.insert(tk.END, cmd_str)
        self.cmd_preview.config(state=tk.DISABLED)

    def browse_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv")])
        if file_path:
            self.input_file.set(file_path)
            base, ext = os.path.splitext(file_path)
            self.output_file.set(base + "_converted.mp4")
            self.update_resolution_options(file_path)

    def browse_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".mp4",
                                                filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("MKV files", "*.mkv"), ("All files", "*.*")])
        if file_path:
            self.output_file.set(file_path)

    def on_drop(self, event):
        file_path = event.data.strip('{}')
        if os.path.isfile(file_path):
            self.input_file.set(file_path)
            # Suggest output file
            base, ext = os.path.splitext(file_path)
            self.output_file.set(base + "_converted.mp4")
            self.update_resolution_options(file_path)
        else:
            messagebox.showwarning("Warning", "Dropped item is not a file")

    

    def convert(self):
        input_file = self.input_file.get()
        output_file = self.output_file.get()
        resolution = self.resolution.get()
        format_name = self.format_name.get()
        
        codec = self.FORMAT_MAP.get(format_name, ("libx264", ".mp4"))[0]

        if not input_file or not output_file:
            messagebox.showerror("Error", "Please specify input and output files")
            return

        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist")
            return

        # FFmpeg command
        cmd = ["ffmpeg", "-i", input_file]
        if resolution != "original":
            cmd.extend(["-vf", f"scale={resolution}"])
        cmd.extend(["-c:v", codec, "-c:a", "aac", "-y", output_file])

        try:
            subprocess.run(cmd, check=True)
            messagebox.showinfo("Success", f"Conversion completed! Output: {output_file}")
            # Open the output folder
            os.startfile(os.path.dirname(output_file))
            self.clear_fields()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")
        except FileNotFoundError:
            messagebox.showerror("Error", "FFmpeg not found. Please install FFmpeg.")

    def get_video_resolution(self, file_path):
        try:
            # Clean up path (handles curly braces from drag-and-drop)
            file_path = file_path.strip('{}')
            cmd = [
                "ffprobe", "-v", "error", "-select_streams", "v:0", 
                "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", 
                file_path
            ]
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
            # Use regex to find WxH in the output (handles multi-line or unexpected output)
            match = re.search(r'(\d+)x(\d+)', output)
            if match:
                return int(match.group(1)), int(match.group(2))
        except Exception as e:
            # Silent fallback if ffprobe is missing or file is invalid
            pass
        return None, None

    def update_resolution_options(self, file_path):
        width, height = self.get_video_resolution(file_path)
        if width and height:
            filtered_resolutions = ["original"]
            orig_max = max(width, height)
            for res in self.RESOLUTIONS:
                if res == "original":
                    continue
                try:
                    w, h = map(int, res.split('x'))
                    preset_max = max(w, h)
                    # Keep if the preset's largest dimension is not an upscale
                    if preset_max <= orig_max:
                        filtered_resolutions.append(res)
                except ValueError:
                    continue
            
            self.resolution_combo['values'] = filtered_resolutions
            if self.resolution.get() not in filtered_resolutions:
                self.resolution.set("original")
        else:
            self.resolution_combo['values'] = self.RESOLUTIONS

    def clear_fields(self):
        self.input_file.set("")
        self.output_file.set("")
        self.resolution.set("original")
        self.resolution_combo['values'] = self.RESOLUTIONS

if __name__ == "__main__":
    try:
        app = VideoConverter()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed by user.")

