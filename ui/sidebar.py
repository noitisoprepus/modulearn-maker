import customtkinter
import tkinter.ttk as ttk

class SidebarFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Modules")
        self.label.grid(row=0, column=0, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="Add Module", command=self.app.add_module)
        self.add_button.grid(row=1, column=0, pady=(0, 8))

        # Subframe for treeview
        tree_container = customtkinter.CTkFrame(self)
        tree_container.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Treeview widget
        self.module_tree = ttk.Treeview(tree_container)
        self.module_tree.grid(row=0, column=0, sticky="nsew")
        self.module_tree.bind("<<TreeviewSelect>>", self.on_select)

        # Scrollbar for the Treeview
        scrollbar = customtkinter.CTkScrollbar(tree_container, command=self.module_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.module_tree.configure(yscrollcommand=scrollbar.set)

    def on_select(self, event):
        item = self.module_tree.focus()
        parent = self.module_tree.parent(item)

        if not parent:
            index = self.module_tree.index(item)
            self.app.main_frame.show_module_editor(index)
        else:
            module_index = self.module_tree.index(parent)
            topic_index = self.module_tree.index(item)
            self.app.main_frame.show_topic_editor(module_index, topic_index)
