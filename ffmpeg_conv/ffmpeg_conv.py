import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
from tkinterdnd2 import TkinterDnD, DND_FILES

class VideoConverter(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("FFmpeg Video Converter")
        self.geometry("600x450")

        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.resolution = tk.StringVar(value="1920x1080")
        self.codec = tk.StringVar(value="libx264")

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

        # Resolution
        tk.Label(self, text="Resolution:").pack(pady=5)
        self.resolution_combo = ttk.Combobox(self, textvariable=self.resolution,
                                             values=["original", "1280x720", "1920x1080", "3840x2160"])
        self.resolution_combo.pack(pady=5)

        # Video Codec
        tk.Label(self, text="Video Codec:").pack(pady=5)
        self.codec_combo = ttk.Combobox(self, textvariable=self.codec,
                                        values=["libx264", "libx265", "vp9", "libvpx-vp9", "copy"])
        self.codec_combo.pack(pady=5)

        tk.Button(self, text="Convert", command=self.convert).pack(pady=20)

    def browse_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv")])
        if file_path:
            self.input_file.set(file_path)
            base, ext = os.path.splitext(file_path)
            self.output_file.set(base + "_converted.mp4")

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
        else:
            messagebox.showwarning("Warning", "Dropped item is not a file")

    def on_drop(self, event):
        file_path = event.data.strip('{}')
        if os.path.isfile(file_path):
            self.input_file.set(file_path)
            # Suggest output file
            base, ext = os.path.splitext(file_path)
            self.output_file.set(base + "_converted.mp4")
        else:
            messagebox.showwarning("Warning", "Dropped item is not a file")

    def convert(self):
        input_file = self.input_file.get()
        output_file = self.output_file.get()
        resolution = self.resolution.get()
        codec = self.codec.get()

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
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")
        except FileNotFoundError:
            messagebox.showerror("Error", "FFmpeg not found. Please install FFmpeg.")

if __name__ == "__main__":
    app = VideoConverter()
    app.mainloop()

