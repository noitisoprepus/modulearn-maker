import os
import re
import shutil
import customtkinter
from tkinter import StringVar, filedialog
from PIL import Image

class SectionEditorFrame(customtkinter.CTkFrame):
    """Frame to edit a specific section depending on its type."""
    def __init__(self, master, section_data, app, on_update=None):
        super().__init__(master)
        self.app = app
        self.section_data = section_data
        self.on_update = on_update or (lambda: None)

        self.grid_columnconfigure(0, weight=1)
        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        st = self.section_data.get("type", "content")
        if st == "text":
            self.build_text_editor("Content", 300)
        elif st == "image":
            self.build_image_editor()
        elif st in ("trivia", "remember"):
            self.build_text_editor(st.capitalize(), 150)
        elif st == "active-recall":
            self.build_trivia_editor()
        else:
            self.build_text_editor("Unknown", 0)

    def build_text_editor(self, label_text, height):
        label = customtkinter.CTkLabel(self, text=label_text)
        label.grid(row=0, column=0, sticky="w", pady=4)

        content_var = StringVar(value=self.section_data.get("content", ""))

        entry = customtkinter.CTkTextbox(self, height=height)
        entry.insert("1.0", content_var.get())
        entry.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)

        def on_change(_=None):
            self.section_data["content"] = entry.get("1.0", "end-1c")
            self.on_update()

        entry.bind("<KeyRelease>", on_change)

    def build_trivia_editor(self):
        qv = StringVar(value=self.section_data.get("question", ""))
        av = StringVar(value=self.section_data.get("answer", ""))
        customtkinter.CTkLabel(self, text="Active Recall Question").grid(row=0, column=0, sticky="w", pady=(4,0))
        qent = customtkinter.CTkEntry(self, textvariable=qv)
        qent.grid(row=1, column=0, sticky="ew", padx=4)
        customtkinter.CTkLabel(self, text="Answer").grid(row=2, column=0, sticky="w", pady=(8,0))
        aent = customtkinter.CTkEntry(self, textvariable=av)
        aent.grid(row=3, column=0, sticky="ew", padx=4)

        def upd():
            self.section_data["question"] = qv.get()
            self.section_data["answer"] = av.get()
            self.on_update()

        qent.bind("<KeyRelease>", lambda _: upd())
        aent.bind("<KeyRelease>", lambda _: upd())

    def build_image_editor(self):
        customtkinter.CTkLabel(self, text="Image").grid(row=0, column=0, sticky="w", pady=(4,2))
        self.preview_label = customtkinter.CTkLabel(self, text="No image selected", anchor="center")
        self.preview_label.grid(row=1, column=0, pady=4)

        def choose_image():
            file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.gif")])
            if not file_path:
                return

            media_dir = self.app.media_dir or os.path.join(self.app.temp_dir, "media")
            os.makedirs(media_dir, exist_ok=True)
            self.app.media_dir = media_dir

            orig = os.path.basename(file_path)
            name, ext = os.path.splitext(orig)
            safe = re.sub(r'[^a-zA-Z0-9_-]', '_', name).lower()
            dest = os.path.join(media_dir, safe + ext.lower())
            shutil.copy(file_path, dest)

            self.section_data["imgSrc"] = safe + ext.lower()
            self.on_update()
            load_preview(dest)

        def load_preview(path):
            try:
                img = Image.open(path)
                img.thumbnail((256,256))
                self.tk_image = customtkinter.CTkImage(light_image=img, size=img.size)
                self.preview_label.configure(image=self.tk_image, text="")
            except Exception as e:
                self.preview_label.configure(text=f"Error loading image:\n{e}", image="")

        if self.section_data.get("imgSrc"):
            abs_path = os.path.join(self.app.temp_dir, self.section_data["imgSrc"])
            if os.path.exists(abs_path):
                load_preview(abs_path)

        customtkinter.CTkButton(self, text="Upload Image", command=choose_image).grid(row=2, column=0, pady=6)
        customtkinter.CTkLabel(self, text="Caption").grid(row=3, column=0, sticky="w", pady=(4,2))
        capvar = StringVar(value=self.section_data.get("caption", ""))
        capent = customtkinter.CTkEntry(self, textvariable=capvar)
        capent.grid(row=4, column=0, sticky="ew", padx=4)

        def upd_cap():
            self.section_data["caption"] = capvar.get()
            self.on_update()

        capent.bind("<KeyRelease>", lambda _: upd_cap())

class SectionListFrame(customtkinter.CTkScrollableFrame):
    """Scrollable container of SectionEditorFrames"""
    def __init__(self, master, section_list, app, on_update=None):
        super().__init__(master)
        self.app = app
        self.section_list = section_list
        self.on_update = on_update or (lambda: None)

        # Manually bind mouse scroll wheel events (For Linux)
        self.bind("<Button-4>", lambda: self._parent_canvas.yview("scroll", -1, "units"))
        self.bind("<Button-5>", lambda: self._parent_canvas.yview("scroll", 1, "units"))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.render_sections()

    def render_sections(self):
        for w in self.winfo_children():
            w.destroy()

        for i, section in enumerate(self.section_list):
            editor = SectionEditorFrame(self, section, self.app, on_update=self.on_update)
            editor.grid(row=i, column=0, sticky="ew", pady=8, padx=8)
