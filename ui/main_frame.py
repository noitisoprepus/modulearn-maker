import customtkinter
from tkinter import StringVar
from ui.section_editor import SectionListFrame
from PIL import Image

class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Editor")
        self.label.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.placeholder = customtkinter.CTkLabel(self, text="")
        self.placeholder.grid(row=1, column=0, sticky="n")

    def clear(self):
        self.placeholder.configure(text="")
        for child in self.winfo_children():
            if child not in [self.label, self.placeholder]:
                child.destroy()

    def show_module_editor(self, module_index):
        self.clear()

        # Module Title
        name_var = StringVar(value=self.app.modules[module_index]["title"])
        name_entry = customtkinter.CTkEntry(self, textvariable=name_var)
        name_entry.grid(row=1, column=0, sticky="ew", padx=4)

        info_label = customtkinter.CTkLabel(self, text="Press Enter to apply changes to the module title", font=("Arial", 10), text_color="gray")
        info_label.grid(row=2, column=0, sticky="w", padx=4)
        
        def update_name():
            self.app.modules[module_index]["title"] = name_var.get()
            self.app.load_modules(self.app.modules)

        name_entry.bind("<Return>", lambda _: update_name())

        def delete_button_pressed():
            self.app.delete_module(module_index)
            self.clear()
        
        # Delete Button
        delete_image = customtkinter.CTkImage(light_image=Image.open("assets/icon_delete.png"))
        delete_button = customtkinter.CTkButton(
            self, 
            image=delete_image, 
            text="", 
            command=delete_button_pressed, 
            width=20, 
            fg_color="white", 
            hover_color="gray", 
            border_color="gray", 
            border_width=2
        )
        delete_button.grid(row=1, column=1, padx=(0, 4))

        def add_topic_button_pressed():
            self.app.add_topic(module_index)

        # Add Topic Button
        add_topic_button = customtkinter.CTkButton(self, text="Add Topic", command=add_topic_button_pressed)
        add_topic_button.grid(row=3, column=0, pady=4, sticky="n")

    def show_topic_editor(self, module_index, topic_index):
        self.clear()

        # Topic Title
        name_var = StringVar(value=self.app.modules[module_index]["topics"][topic_index]["title"])
        name_entry = customtkinter.CTkEntry(self, textvariable=name_var)
        name_entry.grid(row=1, column=0, sticky="ew", padx=4)

        info_label = customtkinter.CTkLabel(self, text="Press Enter to apply changes to the topic title", font=("Arial", 10), text_color="gray")
        info_label.grid(row=2, column=0, sticky="w", padx=4)
        
        def update_name():
            self.app.modules[module_index]["topics"][topic_index]["title"] = name_var.get()
            self.app.load_modules(self.app.modules)

        name_entry.bind("<Return>", lambda _: update_name())

        def delete_button_pressed():
            self.app.delete_topic(module_index, topic_index)
            self.show_module_editor(module_index=module_index)
        
        # Delete Button
        delete_image = customtkinter.CTkImage(light_image=Image.open("assets/icon_delete.png"))
        delete_button = customtkinter.CTkButton(
            self, 
            image=delete_image, 
            text="", 
            command=delete_button_pressed, 
            width=20, 
            fg_color="white", 
            hover_color="gray", 
            border_color="gray", 
            border_width=2
        )
        delete_button.grid(row=1, column=1, padx=(0, 4))

        # Section Selection
        section_type = StringVar(value="text")

        module = self.app.modules[module_index]
        topic = module["topics"][topic_index]
        topic.setdefault("sections", [])
        section_list = topic["sections"]

        def add_section():
            section_data = {"type": section_type.get()}
            if section_type.get() == "image":
                section_data.update({"imgSrc": ""})
            elif section_type.get() == "active-recall":
                section_data.update({"question": "", "answer": ""})
            else:
                section_data.update({"content": ""})

            section_list.append(section_data)
            self.show_topic_editor(module_index, topic_index)

        def delete_section(index):
            del section_list[index]
            self.show_topic_editor(module_index, topic_index)

        types = ["text", "image", "trivia", "remember", "active-recall"]

        # Create a sub-frame to center dropdown and button
        button_row = customtkinter.CTkFrame(self, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=2, pady=4)

        button_row.grid_columnconfigure(0, weight=1)
        button_row.grid_columnconfigure(1, weight=1)
        button_row.grid_columnconfigure(2, weight=1)

        # Centered widgets
        dropdown = customtkinter.CTkOptionMenu(button_row, values=types, variable=section_type)
        dropdown.grid(row=0, column=0, padx=8)

        btn = customtkinter.CTkButton(button_row, text="Add Section", command=add_section)
        btn.grid(row=0, column=1, padx=8)

        # Render frame for showing list of sections
        section_frame = SectionListFrame(self, section_list, self.app, on_delete=delete_section)
        section_frame.grid(row=4, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")

