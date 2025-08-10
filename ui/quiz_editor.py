import os
import re
import shutil
import customtkinter
from tkinter import StringVar, filedialog
from PIL import Image

class QuizQuestionEditorFrame(customtkinter.CTkFrame):
    def __init__(self, master, question_index, question_data, app, on_update=None):
        super().__init__(master)
        self.app = app
        self.question_index = question_index
        self.question_data = question_data
        self.on_update = on_update or (lambda: None)

        self.grid_columnconfigure(1, weight=1)
        self.build_ui()

    def build_ui(self):
        # Label
        question_label = customtkinter.CTkLabel(self, text=f"QUESTION {self.question_index + 1}", text_color="green")
        question_label.grid(row=0, column=0, padx=4, pady=(8, 0), sticky="w")

        # Optional Image
        customtkinter.CTkLabel(self, text="(Optional) Image").grid(row=1, column=0, sticky="w", padx=4, pady=(4, 0))
        self.preview_label = customtkinter.CTkLabel(self, text="No image selected", anchor="center")
        self.preview_label.grid(row=2, column=0, columnspan=2, pady=4)

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

            self.question_data["imgSrc"] = safe + ext.lower()
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

        if self.question_data.get("imgSrc"):
            abs_path = os.path.join(self.app.temp_dir, "media", self.question_data["imgSrc"])
            if os.path.exists(abs_path):
                load_preview(abs_path)

        # Upload Image button
        customtkinter.CTkButton(self, text="Upload Image", command=choose_image).grid(row=3, column=0, columnspan=2)

        # Image Caption
        customtkinter.CTkLabel(self, text="(Optional) Caption").grid(row=4, column=0, padx=4, pady=(4, 0), sticky="w")
        caption_var = StringVar(value=self.question_data.get("caption", ""))
        caption_entry = customtkinter.CTkEntry(self, textvariable=caption_var)
        caption_entry.grid(row=5, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 4))

        # Image Attribution
        customtkinter.CTkLabel(self, text="(Optional) Attribution").grid(row=6, column=0, padx=4, pady=(4, 0), sticky="w")
        attribution_var = StringVar(value=self.question_data.get("attribution", ""))
        attribution_entry = customtkinter.CTkEntry(self, textvariable=attribution_var)
        attribution_entry.grid(row=7, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 4))

        def update_caption():
            self.question_data["caption"] = caption_var.get()
            self.on_update()

        def update_attribution():
            self.question_data["attribution"] = attribution_var.get()
            self.on_update()

        caption_entry.bind("<KeyRelease>", lambda _: update_caption())
        attribution_entry.bind("<KeyRelease>", lambda _: update_attribution())

        # Question
        customtkinter.CTkLabel(self, text="Question").grid(row=8, column=0, sticky="w", padx=4, pady=(4, 0))
        question_var = StringVar(value=self.question_data.get("question", ""))
        question_entry = customtkinter.CTkEntry(self, textvariable=question_var)
        question_entry.grid(row=9, column=0, columnspan=2, padx=4, sticky="ew")

        # Choices
        choices = ["A", "B", "C", "D"]
        self.choice_vars = {}
        for i, letter in enumerate(choices):
            customtkinter.CTkLabel(self, text=f"{letter}").grid(row=10+i, column=0, padx=4, pady=(4, 0), sticky="e")
            var = StringVar(value=self.question_data.get("choices", {}).get(letter, ""))
            entry = customtkinter.CTkEntry(self, textvariable=var)
            entry.grid(row=10+i, column=1, padx=4, sticky="ew")
            self.choice_vars[letter] = var

        def update_question():
            self.question_data["question"] = question_var.get()
            self.question_data["choices"] = {k: v.get() for k, v in self.choice_vars.items()}
            self.on_update()
        
        # Bind events to Question fields
        question_entry.bind("<KeyRelease>", lambda _: update_question())
        for var in self.choice_vars.values():
            var.trace_add("write", lambda *_: update_question())

        def update_answer(choice):
            self.question_data["answer"] = choice
            self.on_update()
        
        # Correct Answer
        customtkinter.CTkLabel(self, text="Answer").grid(row=(10+len(choices)), column=0, padx=4, pady=(4, 0), sticky="e")
        answer_var = StringVar(value=self.question_data.get("answer", ""))
        answer_dropdown = customtkinter.CTkOptionMenu(self, values=choices, variable=answer_var, command=update_answer)
        answer_dropdown.grid(row=(10+len(choices)), column=1, padx=4, sticky="ew")

class QuizListFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, assessment_list, app, on_update=None, on_delete=None):
        super().__init__(master)
        self.app = app
        self.assessment_list = assessment_list
        self.on_update = on_update or (lambda: None)
        self.on_delete = on_delete or (lambda index: None)

        # Manually bind mouse scroll wheel events (For Linux)
        self.bind("<Button-4>", lambda _: self._parent_canvas.yview("scroll", -1, "units"))
        self.bind("<Button-5>", lambda _: self._parent_canvas.yview("scroll", 1, "units"))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.render_questions()

    def render_questions(self):
        for widget in self.winfo_children():
            widget.destroy()

        for i, question in enumerate(self.assessment_list):
            # Question Fields
            editor = QuizQuestionEditorFrame(self, i, question, self.app, on_update=self.on_update)
            editor.grid(row=i, column=0, sticky="ew", padx=8, pady=(8, 0))

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
