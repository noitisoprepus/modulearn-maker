import os
import re
import shutil
import customtkinter
from tkinter import StringVar, BooleanVar, filedialog
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

        section_type = self.section_data.get("type", "content")
        if section_type == "text":
            self.build_text_editor("Text", 150, show_header=True)
        elif section_type == "list":
            self.build_list_editor()
        elif section_type == "image":
            self.build_image_editor()
        elif section_type in ("trivia", "remember"):
            self.build_text_editor(section_type.capitalize(), 50)
        elif section_type == "active-recall":
            self.build_qna_editor()
        else:
            self.build_text_editor("Unknown", 0)

    def build_text_editor(self, label_text, height, show_header=False):
        # Label
        customtkinter.CTkLabel(self, text=label_text.upper(), text_color="green").grid(row=0, column=0, padx=4, pady=(4, 0), sticky="w")

        # Header
        if (show_header):
            customtkinter.CTkLabel(self, text="(Optional) Header").grid(row=1, column=0, sticky="w", padx=4, pady=(4, 0))
            header_var = StringVar(value=self.section_data.get("header", ""))
            header_entry = customtkinter.CTkEntry(self, textvariable=header_var)
            header_entry.grid(row=2, column=0, padx=4, sticky="ew")

            def update_header():
                self.section_data["header"] = header_var.get()
                self.on_update()

            header_entry.bind("<KeyRelease>", lambda _: update_header())

        # Text Content
        customtkinter.CTkLabel(self, text="Content").grid(row=3, column=0, sticky="w", padx=4, pady=(4, 0))
        content_var = StringVar(value=self.section_data.get("content", ""))
        content_entry = customtkinter.CTkTextbox(self, wrap="word", height=height)
        content_entry.insert("1.0", content_var.get())
        content_entry.grid(row=4, column=0, sticky="nsew", padx=4, pady=(0, 4))

        def update_content():
            self.section_data["content"] = content_entry.get("1.0", "end-1c")
            self.on_update()
        
        content_entry.bind("<KeyRelease>", lambda _: update_content())

    def build_list_editor(self):
        # Clear existing widgets before re-rendering
        for widget in self.winfo_children():
            widget.destroy()
            
        # Label
        customtkinter.CTkLabel(self, text="LIST", text_color="green").grid(row=0, column=0, padx=4, pady=(4, 0), sticky="w")

        categories = ["unordered", "ordered"]
        entry_list = self.section_data.get("entries", [""])

        def add_entry():
            entry_list.append("")
            self.section_data["entries"] = entry_list
            self.build_list_editor()

        def delete_entry(index):
            del entry_list[index]
            self.section_data["entries"] = entry_list
            self.build_list_editor()

        def update_category(choice):
            self.section_data["category"] = choice

        def update_entry_text(index, text):
            entry_list[index] = text
            self.section_data["entries"] = entry_list

        # Create a sub-frame for the dropdown and button
        button_row = customtkinter.CTkFrame(self, fg_color="transparent")
        button_row.grid(row=1, column=0, columnspan=2, pady=4, sticky="w")

        # Category dropdown
        category_var = StringVar(value=self.section_data.get("category", "unordered"))
        category_dropdown = customtkinter.CTkOptionMenu(button_row, values=categories, variable=category_var, command=update_category)
        category_dropdown.grid(row=0, column=0, padx=8, sticky="w")

        # Toggle for hasHeader
        hasHeader_var = BooleanVar(value=self.section_data.get("hasHeader", False))
        
        def toggle_has_header():
            self.section_data["hasHeader"] = hasHeader_var.get()
        
        hasHeader_checkbox = customtkinter.CTkCheckBox(button_row, text="Has Header", variable=hasHeader_var, command=toggle_has_header)
        hasHeader_checkbox.grid(row=0, column=1, padx=8, sticky="w")
        
        # Add entry button
        add_button = customtkinter.CTkButton(self, text="Add Entry", command=add_entry)
        add_button.grid(row=2, column=0, padx=8, sticky="w")

        # Entries list
        for index, value in enumerate(entry_list):
            entry_frame = customtkinter.CTkFrame(self, fg_color="transparent")
            entry_frame.grid(row=3 + index, column=0, columnspan=2, pady=2, sticky="ew")
            entry_frame.grid_columnconfigure(0, weight=1)
            entry_frame.grid_columnconfigure(1, weight=0)

            # Text entry for list item
            entry_content = customtkinter.CTkTextbox(entry_frame, wrap="word", height=80)
            entry_content.insert("1.0", value)
            entry_content.grid(row=0, column=0, padx=4, sticky="ew")

            # Update on key release
            def bind_textbox(widget, index):
                def on_change(event):
                    entry_value = widget.get("1.0", "end-1c")  # Remove trailing newline
                    entry_list[index] = entry_value
                    self.section_data["entries"] = entry_list
                widget.bind("<KeyRelease>", on_change)
            bind_textbox(entry_content, index)
            
            # Delete button
            delete_button = customtkinter.CTkButton(entry_frame, text="Remove", width=60, command=lambda i=index: delete_entry(i))
            delete_button.grid(row=0, column=1, padx=4, sticky="e")

    def build_qna_editor(self):
        # Label
        customtkinter.CTkLabel(self, text="ACTIVE RECALL", text_color="green").grid(row=0, column=0, sticky="w", padx=4, pady=(4, 0))

        # Question
        question_var = StringVar(value=self.section_data.get("question", ""))
        customtkinter.CTkLabel(self, text="Question").grid(row=1, column=0, padx=4, pady=(4, 0), sticky="w")
        question_entry = customtkinter.CTkEntry(self, textvariable=question_var)
        question_entry.grid(row=2, column=0, sticky="ew", padx=4)
        
        # Answer
        answer_var = StringVar(value=self.section_data.get("answer", ""))
        customtkinter.CTkLabel(self, text="Answer").grid(row=3, column=0, padx=4, pady=(4, 0), sticky="w")
        answer_entry = customtkinter.CTkEntry(self, textvariable=answer_var)
        answer_entry.grid(row=4, column=0, sticky="ew", padx=4, pady=(0, 4))

        def update_qna():
            self.section_data["question"] = question_var.get()
            self.section_data["answer"] = answer_var.get()
            self.on_update()

        question_entry.bind("<KeyRelease>", lambda _: update_qna())
        answer_entry.bind("<KeyRelease>", lambda _: update_qna())

    def build_image_editor(self):
        # Label
        customtkinter.CTkLabel(self, text="IMAGE", text_color="green").grid(row=0, column=0, sticky="w", padx=4, pady=(4, 0))

        # Preview Image Label
        self.preview_label = customtkinter.CTkLabel(self, text="No image selected", anchor="center")
        self.preview_label.grid(row=1, column=0, pady=4)

        # Image Selection
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

        # Image preview
        def load_preview(path):
            try:
                img = Image.open(path)
                img.thumbnail((256,256))
                self.tk_image = customtkinter.CTkImage(light_image=img, size=img.size)
                self.preview_label.configure(image=self.tk_image, text="")
            except Exception as e:
                self.preview_label.configure(text=f"Error loading image:\n{e}", image="")

        if self.section_data.get("imgSrc"):
            abs_path = os.path.join(self.app.temp_dir, "media", self.section_data["imgSrc"])
            if os.path.exists(abs_path):
                load_preview(abs_path)

        # Upload Image button
        customtkinter.CTkButton(self, text="Upload Image", command=choose_image).grid(row=2, column=0)
        
        # Image Caption
        customtkinter.CTkLabel(self, text="(Optional) Caption").grid(row=3, column=0, padx=4, pady=(4, 0), sticky="w")
        caption_var = StringVar(value=self.section_data.get("caption", ""))
        caption_entry = customtkinter.CTkEntry(self, textvariable=caption_var)
        caption_entry.grid(row=4, column=0, sticky="ew", padx=4, pady=(0, 4))

        # Image Attribution
        customtkinter.CTkLabel(self, text="(Optional) Attribution").grid(row=5, column=0, padx=4, pady=(4, 0), sticky="w")
        attribution_var = StringVar(value=self.section_data.get("caption", ""))
        attribution_entry = customtkinter.CTkEntry(self, textvariable=caption_var)
        attribution_entry.grid(row=6, column=0, sticky="ew", padx=4, pady=(0, 4))

        def update_caption():
            self.section_data["caption"] = caption_var.get()
            self.on_update()

        def update_attribution():
            self.section_data["attribution"] = attribution_var.get()
            self.on_update()

        caption_entry.bind("<KeyRelease>", lambda _: update_caption())
        attribution_entry.bind("<KeyRelease>", lambda _: update_attribution())

class SectionListFrame(customtkinter.CTkScrollableFrame):
    """Scrollable container of SectionEditorFrames"""
    def __init__(self, master, section_list, app, on_update=None, on_delete=None):
        super().__init__(master)
        self.app = app
        self.section_list = section_list
        self.on_update = on_update or (lambda: None)
        self.on_delete = on_delete or (lambda index: None)

        # Manually bind mouse scroll wheel events (For Linux)
        self.bind("<Button-4>", lambda _: self._parent_canvas.yview("scroll", -1, "units"))
        self.bind("<Button-5>", lambda _: self._parent_canvas.yview("scroll", 1, "units"))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.render_sections()

    def render_sections(self):
        for widget in self.winfo_children():
            widget.destroy()

        for i, section in enumerate(self.section_list):
            # Editor Fields
            editor = SectionEditorFrame(self, section, self.app, on_update=self.on_update)
            editor.grid(row=i, column=0, sticky="ew", pady=(4, 0), padx=16)

            # Delete Buttons
            delete_image = customtkinter.CTkImage(light_image=Image.open(self.app.resource_path("assets/icon_delete.png")))
            delete_button = customtkinter.CTkButton(
                self, 
                image=delete_image, 
                text="", 
                command=lambda index=i: self.on_delete(index), 
                width=20, 
                fg_color="white", 
                hover_color="gray", 
                border_color="gray", 
                border_width=2
            )
            delete_button.grid(row=i, column=1, padx=(0, 4))
