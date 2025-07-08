import os
import json
import tempfile
import zipfile
import shutil
import customtkinter
from tkinter import filedialog, messagebox

from ui.sidebar import SidebarFrame
from ui.main_frame import MainFrame

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("ModuLearn Maker")
        self.geometry("1024x640")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.grid_columnconfigure(4, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.modules = []

        # Top control buttons container
        top_controls = customtkinter.CTkFrame(self, fg_color="transparent")
        top_controls.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 0))

        # Top control buttons
        self.button_new = customtkinter.CTkButton(top_controls, text="New", width=48, command=self.new_file)
        self.button_new.pack(side="left", padx=(0, 4))
        self.button_open = customtkinter.CTkButton(top_controls, text="Open", width=48, command=self.open_file)
        self.button_open.pack(side="left", padx=(0, 4))
        self.button_save = customtkinter.CTkButton(top_controls, text="Save", width=48, command=self.save_file)
        self.button_save.pack(side="left")

        # Layout frames
        self.sidebar_frame = SidebarFrame(self, self)
        self.sidebar_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=3)
        self.main_frame = MainFrame(self, self)
        self.main_frame.grid(row=1, column=4, padx=10, pady=10, sticky="nsew")

        self.temp_dir = tempfile.mkdtemp(prefix="modulearn-maker_")
        self.media_dir = None

    def on_close(self):
        """Handle graceful exit."""
        self.cleanup_temp_dir()
        self.destroy()

    def new_file(self):
        """Start a new module session."""
        self.cleanup_temp_dir()
        self.temp_dir = tempfile.mkdtemp(prefix="modulearn-maker_")
        self.modules = []
        self.sidebar_frame.load_modules(self.modules)
        messagebox.showinfo("Info", "New module set created.")

    def open_file(self):
        """Open and extract a zipped module set."""
        file_path = filedialog.askopenfilename(filetypes=[("ZIP File", "*.zip")])
        if not file_path:
            return

        self.cleanup_temp_dir()

        try:
            self.temp_dir = tempfile.mkdtemp(prefix="modulearn-maker_")
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)

            # Load all JSON files in the root as modules
            module_files = sorted([
                f for f in os.listdir(self.temp_dir)
                if f.endswith('.json') and os.path.isfile(os.path.join(self.temp_dir, f))
            ], key=lambda f: int(f.split("_")[1].split(".")[0]))

            self.modules = []
            for file in module_files:
                with open(os.path.join(self.temp_dir, file), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.modules.append(data)

            # Handle media directory
            media_path = os.path.join(self.temp_dir, "media")
            if os.path.exists(media_path) and os.path.isdir(media_path):
                self.media_dir = media_path
            else:
                self.media_dir = None

            self.sidebar_frame.load_modules(self.modules)
            messagebox.showinfo("Success", f"Loaded {len(self.modules)} modules.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def save_file(self):
        """Save current modules into a new ZIP file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP File", "*.zip")])
        if not file_path:
            return

        try:
            # Ensure temp_dir exists
            if not os.path.exists(self.temp_dir):
                messagebox.showerror("Error", "No modules data initialized.")
                return

            # Remove old JSON files to avoid duplication
            for f in os.listdir(self.temp_dir):
                if f.endswith(".json"):
                    os.remove(os.path.join(self.temp_dir, f))

            # Write updated module JSON files
            for i, module in enumerate(self.modules):
                filename = f"module_{i}.json"
                with open(os.path.join(self.temp_dir, filename), "w", encoding="utf-8") as f:
                    json.dump(module, f, indent=2, ensure_ascii=True)

            # Bundle temp_dir into zip
            with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for foldername, _, filenames in os.walk(self.temp_dir):
                    for filename in filenames:
                        file_path_in_temp = os.path.join(foldername, filename)
                        arcname = os.path.relpath(file_path_in_temp, self.temp_dir)
                        zipf.write(file_path_in_temp, arcname)

            messagebox.showinfo("Success", f"Modules saved to ZIP:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def cleanup_temp_dir(self):
        """Remove temporary directory and all contents."""
        if hasattr(self, "temp_dir") and self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned temp dir: {self.temp_dir}")
            except Exception as e:
                print(f"Error cleaning temp dir: {e}")
            finally:
                self.temp_dir = None

if __name__ == "__main__":
    app = App()
    app.mainloop()
