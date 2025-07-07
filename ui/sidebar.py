import customtkinter
import tkinter.ttk as ttk

class SidebarFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Modules")
        self.label.grid(row=0, column=0, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="Add Module", command=self.add_module)
        self.add_button.grid(row=1, column=0, pady=(0, 8))

        self.module_tree = ttk.Treeview(self)
        self.module_tree.grid(row=2, column=0, sticky="nsew")
        self.module_tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_modules(self, modules):
        self.module_tree.delete(*self.module_tree.get_children())
        for i, module in enumerate(modules):
            module_id = self.module_tree.insert("", "end", text=module["title"], open=True)
            for topic in module.get("topics", []):
                self.module_tree.insert(module_id, "end", text=topic["title"])

    def add_module(self):
        new_module = {"title": f"Untitled Module {len(self.app.modules)}", "topics": []}
        self.app.modules.append(new_module)
        self.load_modules(self.app.modules)

    def on_select(self, event):
        item = self.module_tree.focus()
        parent = self.module_tree.parent(item)

        if not parent:
            index = self.module_tree.index(item)
            self.app.main_frame.show_add_topic(index)
        else:
            module_index = self.module_tree.index(parent)
            topic_index = self.module_tree.index(item)
            self.app.main_frame.show_add_section(module_index, topic_index)
