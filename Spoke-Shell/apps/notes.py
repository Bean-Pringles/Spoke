import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class NoteTab:
    def __init__(self, master, filename=None):
        self.frame = ttk.Frame(master)
        self.filename = filename
        self.text = tk.Text(self.frame, undo=True, wrap="word", bg="#101924", fg="#c0d9ff",
                            insertbackground="#70a0ff", selectbackground="#334466",
                            font=("Consolas", 12), padx=10, pady=10)
        self.scrollbar = ttk.Scrollbar(self.frame, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text.bind("<<Modified>>", self.on_modified)
        self.dirty = False

    def on_modified(self, event=None):
        self.dirty = True
        self.text.edit_modified(0)

    def get_content(self):
        return self.text.get(1.0, "end-1c")

    def set_content(self, content):
        self.text.delete(1.0, "end")
        self.text.insert("end", content)
        self.dirty = False

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spoke Notes")
        self.root.geometry("800x600")
        self.root.configure(bg="#0e1624")

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#0e1624", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1c2b3a", foreground="#70a0ff", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#112233")])

        self.note_tabs = []

        self.create_menu()
        self.new_note()

    def create_menu(self):
        menubar = tk.Menu(self.root, bg="#0e1624", fg="#70a0ff", activebackground="#182635", activeforeground="white")
        filemenu = tk.Menu(menubar, tearoff=0, bg="#0e1624", fg="#70a0ff")
        filemenu.add_command(label="New", command=self.new_note)
        filemenu.add_command(label="Open", command=self.open_note)
        filemenu.add_command(label="Save", command=self.save_note)
        filemenu.add_command(label="Save As", command=self.save_note_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = tk.Menu(menubar, tearoff=0, bg="#0e1624", fg="#70a0ff")
        editmenu.add_command(label="Find", command=self.find_text)
        editmenu.add_command(label="Word Count", command=self.word_count)
        menubar.add_cascade(label="Edit", menu=editmenu)

        viewmenu = tk.Menu(menubar, tearoff=0, bg="#0e1624", fg="#70a0ff")
        viewmenu.add_command(label="Increase Font Size", command=self.increase_font)
        viewmenu.add_command(label="Decrease Font Size", command=self.decrease_font)
        menubar.add_cascade(label="View", menu=viewmenu)

        self.root.config(menu=menubar)

    def current_tab(self):
        tab_index = self.tabs.index("current")
        return self.note_tabs[tab_index] if tab_index < len(self.note_tabs) else None

    def new_note(self):
        note = NoteTab(self.tabs)
        self.note_tabs.append(note)
        self.tabs.add(note.frame, text="Untitled")
        self.tabs.select(len(self.note_tabs) - 1)

    def open_note(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All files", "*.*")])
        if not filepath:
            return
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        note = NoteTab(self.tabs, filename=filepath)
        note.set_content(content)
        self.note_tabs.append(note)
        name = os.path.basename(filepath)
        self.tabs.add(note.frame, text=name)
        self.tabs.select(len(self.note_tabs) - 1)

    def save_note(self):
        tab = self.current_tab()
        if tab.filename:
            with open(tab.filename, "w", encoding="utf-8") as f:
                f.write(tab.get_content())
            tab.dirty = False
        else:
            self.save_note_as()

    def save_note_as(self):
        tab = self.current_tab()
        filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text Files", "*.txt"), ("All files", "*.*")])
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(tab.get_content())
            tab.filename = filepath
            name = os.path.basename(filepath)
            index = self.note_tabs.index(tab)
            self.tabs.tab(index, text=name)
            tab.dirty = False

    def exit_app(self):
        for tab in self.note_tabs:
            if tab.dirty:
                if tab.filename:
                    with open(tab.filename, "w", encoding="utf-8") as f:
                        f.write(tab.get_content())
                    tab.dirty = False
                else:
                    self.tabs.select(self.note_tabs.index(tab))  # Switch to that tab
                    self.save_note_as()
        self.root.destroy()

    def increase_font(self):
        tab = self.current_tab()
        font = tab.text["font"]
        name, size = font.split()
        tab.text.config(font=(name, int(size) + 1))

    def decrease_font(self):
        tab = self.current_tab()
        font = tab.text["font"]
        name, size = font.split()
        tab.text.config(font=(name, max(6, int(size) - 1)))

    def find_text(self):
        tab = self.current_tab()
        if not tab:
            return
        top = tk.Toplevel(self.root)
        top.title("Find")
        top.geometry("300x80")
        top.configure(bg="#0e1624")

        label = tk.Label(top, text="Find:", bg="#0e1624", fg="#70a0ff")
        label.pack(pady=5)
        entry = tk.Entry(top, width=30, bg="#101924", fg="#c0d9ff", insertbackground="#70a0ff")
        entry.pack(pady=5)

        def search():
            tab.text.tag_remove("search", "1.0", tk.END)
            query = entry.get()
            if not query:
                return
            start = "1.0"
            while True:
                start = tab.text.search(query, start, nocase=1, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(query)}c"
                tab.text.tag_add("search", start, end)
                tab.text.tag_config("search", background="#304070")
                start = end

        entry.bind("<Return>", lambda e: search())

    def word_count(self):
        tab = self.current_tab()
        text = tab.get_content()
        words = len(text.split())
        chars = len(text)
        messagebox.showinfo("Word Count", f"Words: {words}\nCharacters: {chars}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()