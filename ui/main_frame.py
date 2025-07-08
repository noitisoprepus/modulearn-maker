import customtkinter
from tkinter import StringVar
from ui.section_editor import SectionListFrame

class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Module Editor")
        self.label.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.placeholder = customtkinter.CTkLabel(self, text="")
        self.placeholder.grid(row=1, column=0, sticky="n")

    def clear(self):
        self.placeholder.configure(text="")
        for child in self.winfo_children():
            if child not in [self.label, self.placeholder]:
                child.destroy()

    def show_add_topic(self, module_index):
        self.clear()
        def add_topic():
            module = self.app.modules[module_index]
            module.setdefault("topics", []).append({"title": f"Topic {len(module['topics'])}", "sections": []})
            self.app.sidebar_frame.load_modules(self.app.modules)

        btn = customtkinter.CTkButton(self, text="Add Topic", command=add_topic)
        btn.grid(row=1, column=0, padx=10, pady=10, sticky="n")

    def show_add_section(self, module_index, topic_index):
        self.clear()
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
            self.show_add_section(module_index, topic_index)

        types = ["text", "image", "trivia", "remember", "active-recall"]

        # Create a sub-frame to center dropdown and button
        button_row = customtkinter.CTkFrame(self, fg_color="transparent")
        button_row.grid(row=1, column=0, columnspan=2, pady=10)

        button_row.grid_columnconfigure(0, weight=1)
        button_row.grid_columnconfigure(1, weight=1)
        button_row.grid_columnconfigure(2, weight=1)

        # Centered widgets
        dropdown = customtkinter.CTkOptionMenu(button_row, values=types, variable=section_type)
        dropdown.grid(row=0, column=0, padx=10)

        btn = customtkinter.CTkButton(button_row, text="Add Section", command=add_section)
        btn.grid(row=0, column=1, padx=10)

        # Render frame for showing list of sections
        section_frame = SectionListFrame(self, section_list, self.app)
        section_frame.grid(row=2, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")

