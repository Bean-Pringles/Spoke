import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk, scrolledtext
import re
import os
import subprocess
import json
import threading

# ------------------------
# Constants & Helpers
# ------------------------

# Spoke keywords for highlighting
SPOKE_KEYWORDS = {
    "let", "print", "input", "clear", "pause", "time", "length",
    "shuffle", "toggle", "swap", "compare", "sleep", "delete",
    "countdown", "function", "random", "quit", "math", "if",
    "else", "while", "for", "return", "true", "false", "null"
}

THEME_PRESETS = {
    "dark": {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "button_bg": "#2e2e2e",
        "select_bg": "#404040",
        "toolbar_bg": "#2b2b2b",
        "sidebar_bg": "#1e1e1e",
        "sidebar_fg": "#ffffff",
        "line_number_bg": "#2a2a2a",
        "line_number_fg": "#888888",
        "highlight_keyword": "#569cd6",
        "highlight_string": "#d69d85",
        "highlight_comment": "#6a9955",
        "highlight_number": "#b5cea8",
        "highlight_operator": "#d4d4d4",
        "highlight_function": "#dcdcaa",
        "error_bg": "#ff0000",
        "warning_bg": "#ffcc00",
        "cursor_color": "#ffffff",
        "select_fg": "#ffffff",
        "select_bg": "#555555",
    },
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "button_bg": "#e0e0e0",
        "select_bg": "#c0c0c0",
        "toolbar_bg": "#f0f0f0",
        "sidebar_bg": "#ffffff",
        "sidebar_fg": "#000000",
        "line_number_bg": "#f0f0f0",
        "line_number_fg": "#666666",
        "highlight_keyword": "#0000ff",
        "highlight_string": "#a31515",
        "highlight_comment": "#008000",
        "highlight_number": "#098658",
        "highlight_operator": "#000000",
        "highlight_function": "#795e26",
        "error_bg": "#ff0000",
        "warning_bg": "#ffcc00",
        "cursor_color": "#000000",
        "select_fg": "#000000",
        "select_bg": "#c0c0c0",
    }
}

CONFIG_FILE = "spoke_editor_config.json"

def load_config():
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except:
        pass

# ------------------------
# Main Editor Tab Class
# ------------------------

class EditorTab(ttk.Frame):
    def __init__(self, parent, theme, filename=None, content=""):
        super().__init__(parent)

        self.theme = theme
        self.filename = filename

        # Create main frame for text editor and line numbers
        self.text_frame = tk.Frame(self)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        # Create scrollbar
        self.vscroll = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Create line numbers widget
        self.line_numbers = tk.Text(self.text_frame, width=4, padx=4, takefocus=0, 
                                   border=0, state='disabled', wrap='none',
                                   background=theme['line_number_bg'],
                                   foreground=theme['line_number_fg'],
                                   font=("Consolas", 12))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Create main text widget
        self.text = tk.Text(self.text_frame, undo=True, wrap='none',
                           font=("Consolas", 12),
                           bg=theme['bg'], fg=theme['fg'], 
                           insertbackground=theme['fg'],
                           yscrollcommand=self.on_text_scroll)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Connect scrollbar to text widget
        self.vscroll.config(command=self.on_scrollbar_scroll)

        # Insert initial content
        if content:
            self.text.insert("1.0", content)
        elif not filename:  # New file, add basic Spoke template
            template = """# Welcome to Spoke!
print (Hello, World!)
"""
            self.text.insert("1.0", template)

        # Create syntax highlighting tags
        self.create_tags()

        # Bind events
        self.text.bind("<<Modified>>", self.on_text_modified)
        self.text.bind("<KeyRelease>", self.on_key_release)
        self.text.bind("<Button-1>", self.on_click)
        self.text.bind("<MouseWheel>", self.on_mouse_wheel)
        self.text.bind("<Button-4>", self.on_mouse_wheel)  # Linux
        self.text.bind("<Button-5>", self.on_mouse_wheel)  # Linux

        # Auto-complete bindings
        self.text.bind("<Control-space>", self.show_autocomplete)
        self.text.bind("<Tab>", self.handle_tab)

        # Initial line number update
        self.update_line_numbers()

    def create_tags(self):
        """Create syntax highlighting tags"""
        self.text.tag_configure("keyword_highlight", foreground=self.theme.get('highlight_keyword', '#569cd6'))
        self.text.tag_configure("string_highlight", foreground=self.theme.get('highlight_string', '#d69d85'))
        self.text.tag_configure("comment_highlight", foreground=self.theme.get('highlight_comment', '#6a9955'))
        self.text.tag_configure("number_highlight", foreground=self.theme.get('highlight_number', '#b5cea8'))
        self.text.tag_configure("function_highlight", foreground=self.theme.get('highlight_function', '#dcdcaa'))

    def on_scrollbar_scroll(self, *args):
        """Handle scrollbar movement"""
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def on_text_scroll(self, first, last):
        """Handle text widget scroll"""
        self.vscroll.set(first, last)
        self.line_numbers.yview_moveto(first)

    def on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.num == 4 or event.delta > 0:
            delta = -1
        else:
            delta = 1
        
        self.text.yview_scroll(delta, "units")
        self.line_numbers.yview_scroll(delta, "units")
        return "break"

    def on_text_modified(self, event=None):
        """Handle text modifications"""
        self.text.edit_modified(False)
        self.update_line_numbers()
        self.highlight_all()

    def on_key_release(self, event=None):
        """Handle key release events"""
        self.update_line_numbers()
        self.highlight_all()

    def on_click(self, event=None):
        """Handle mouse clicks"""
        self.after_idle(self.update_line_numbers)

    def handle_tab(self, event):
        """Handle tab key for auto-indentation"""
        cursor_pos = self.text.index(tk.INSERT)
        line_start = cursor_pos.split('.')[0] + '.0'
        line_content = self.text.get(line_start, cursor_pos)
        
        # Calculate indentation
        indent_level = len(line_content) - len(line_content.lstrip())
        if line_content.strip().endswith('{') or line_content.strip().endswith(':'):
            indent_level += 4
        
        self.text.insert(tk.INSERT, ' ' * 4)  # 4 spaces for tab
        return "break"

    def show_autocomplete(self, event):
        """Show autocomplete suggestions"""
        cursor_pos = self.text.index(tk.INSERT)
        line_start = cursor_pos.split('.')[0] + '.0'
        line_content = self.text.get(line_start, cursor_pos)
        
        # Get the current word
        words = line_content.split()
        if words:
            current_word = words[-1]
            suggestions = []
            
            # Suggest Spoke keywords
            for keyword in SPOKE_KEYWORDS:
                if keyword.startswith(current_word.lower()):
                    suggestions.append(keyword)
            
            if suggestions:
                self.show_suggestion_popup(suggestions[:10])  # Show top 10

    def show_suggestion_popup(self, suggestions):
        """Show autocomplete popup"""
        popup = tk.Toplevel(self)
        popup.wm_overrideredirect(True)
        popup.configure(bg=self.theme['bg'])
        
        # Position popup near cursor
        x, y, _, _ = self.text.bbox(tk.INSERT)
        x += self.text.winfo_rootx()
        y += self.text.winfo_rooty() + 20
        popup.geometry(f"+{x}+{y}")
        
        listbox = tk.Listbox(popup, bg=self.theme['bg'], fg=self.theme['fg'])
        listbox.pack()
        
        for suggestion in suggestions:
            listbox.insert(tk.END, suggestion)
        
        def on_select(event):
            selection = listbox.get(listbox.curselection())
            # Insert the selected suggestion
            cursor_pos = self.text.index(tk.INSERT)
            line_start = cursor_pos.split('.')[0] + '.0'
            line_content = self.text.get(line_start, cursor_pos)
            words = line_content.split()
            if words:
                # Replace the last word
                word_start = cursor_pos.split('.')[0] + '.' + str(len(line_content) - len(words[-1]))
                self.text.delete(word_start, cursor_pos)
                self.text.insert(word_start, selection)
            popup.destroy()
        
        listbox.bind('<Double-Button-1>', on_select)
        listbox.bind('<Return>', on_select)
        listbox.focus_set()
        
        # Auto-destroy popup after 5 seconds
        popup.after(5000, popup.destroy)

    def update_line_numbers(self):
        """Update line numbers display"""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete("1.0", tk.END)
        
        line_count = int(self.text.index('end-1c').split('.')[0])
        line_text = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert("1.0", line_text)
        
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.text.yview()[0])

    def highlight_all(self):
        """Apply syntax highlighting"""
        # Clear existing tags
        for tag in ["keyword_highlight", "string_highlight", "comment_highlight", "number_highlight", "function_highlight"]:
            self.text.tag_remove(tag, "1.0", tk.END)
        
        content = self.text.get("1.0", tk.END)
        
        # Highlight keywords
        for keyword in SPOKE_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, content):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.text.tag_add("keyword_highlight", start_idx, end_idx)
        
        # Highlight strings
        for match in re.finditer(r'"[^"]*"', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text.tag_add("string_highlight", start_idx, end_idx)
        
        for match in re.finditer(r"'[^']*'", content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text.tag_add("string_highlight", start_idx, end_idx)
        
        # Highlight comments
        for match in re.finditer(r'#.*$', content, re.MULTILINE):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text.tag_add("comment_highlight", start_idx, end_idx)
        
        # Highlight numbers
        for match in re.finditer(r'\b\d+\.?\d*\b', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text.tag_add("number_highlight", start_idx, end_idx)
        
        # Highlight function calls (simplified for Spoke)
        for match in re.finditer(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*(?=\s|$)', content):
            word = match.group().strip()
            if word in SPOKE_KEYWORDS:
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()-1}c"
                self.text.tag_add("function_highlight", start_idx, end_idx)

    def get_content(self):
        """Get the content of the text widget"""
        return self.text.get("1.0", tk.END + "-1c")

    def set_content(self, content):
        """Set the content of the text widget"""
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.update_line_numbers()
        self.highlight_all()

# ------------------------
# Main Application Class
# ------------------------

class SpokeEditor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Spoke Code Editor")
        self.geometry("1200x800")

        self.config_data = load_config()
        self.current_theme_name = self.config_data.get("theme", "dark")
        self.theme = THEME_PRESETS.get(self.current_theme_name, THEME_PRESETS["dark"])

        # Check for spoke.py in current directory
        self.spoke_interpreter = self.find_spoke_interpreter()

        self.create_widgets()
        self.create_menu()
        self.bind_shortcuts()
        self.apply_theme()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def find_spoke_interpreter(self):
        """Find spoke.py interpreter"""
        # Check current directory first
        current_dir_spoke = os.path.join(os.getcwd(), "spoke.py")
        if os.path.exists(current_dir_spoke):
            return current_dir_spoke
    
        # Check script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_dir_spoke = os.path.join(script_dir, "spoke.py")
        if os.path.exists(script_dir_spoke):
            return script_dir_spoke
        
        return None

    def create_menu(self):
        menubar = tk.Menu(self)

        # File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        filemenu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        filemenu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        filemenu.add_command(label="Save As...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # Edit menu
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        editmenu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        editmenu.add_separator()
        editmenu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        editmenu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        editmenu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        editmenu.add_separator()
        editmenu.add_command(label="Find & Replace", command=self.open_find_replace_dialog, accelerator="Ctrl+F")
        menubar.add_cascade(label="Edit", menu=editmenu)

        # Run menu
        runmenu = tk.Menu(menubar, tearoff=0)
        runmenu.add_command(label="Run Program", command=self.run_program, accelerator="F5")
        runmenu.add_command(label="Set Spoke Interpreter", command=self.set_spoke_interpreter)
        menubar.add_cascade(label="Run", menu=runmenu)

        # View menu
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Toggle Theme", command=self.switch_theme, accelerator="Ctrl+T")
        viewmenu.add_command(label="Toggle Help Panel", command=self.toggle_help_panel)
        menubar.add_cascade(label="View", menu=viewmenu)

        self.config(menu=menubar)

    def create_widgets(self):
        # Toolbar
        self.toolbar = tk.Frame(self, bd=1, relief=tk.RAISED, bg=self.theme['toolbar_bg'])
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Toolbar buttons
        self.btn_new = tk.Button(self.toolbar, text="New", command=self.new_file, bg=self.theme['button_bg'], fg=self.theme['fg'])
        self.btn_new.pack(side=tk.LEFT, padx=2, pady=2)

        self.btn_open = tk.Button(self.toolbar, text="Open", command=self.open_file, bg=self.theme['button_bg'], fg=self.theme['fg'])
        self.btn_open.pack(side=tk.LEFT, padx=2, pady=2)

        self.btn_save = tk.Button(self.toolbar, text="Save", command=self.save_file, bg=self.theme['button_bg'], fg=self.theme['fg'])
        self.btn_save.pack(side=tk.LEFT, padx=2, pady=2)

        self.btn_close_tab = tk.Button(self.toolbar, text="Close Tab", command=self.close_current_tab, bg=self.theme['button_bg'], fg=self.theme['fg'])
        self.btn_close_tab.pack(side=tk.LEFT, padx=2, pady=2)

        # Separator
        separator = tk.Frame(self.toolbar, width=2, bg=self.theme['toolbar_bg'])
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        self.btn_run = tk.Button(self.toolbar, text="Run", command=self.run_program, bg=self.theme['button_bg'], fg=self.theme['fg'])
        self.btn_run.pack(side=tk.LEFT, padx=2, pady=2)

        self.btn_theme = tk.Button(self.toolbar, text="Theme", command=self.switch_theme, bg=self.theme['button_bg'], fg=self.theme['fg'])
        self.btn_theme.pack(side=tk.LEFT, padx=2, pady=2)

        # Status label for spoke interpreter
        self.status_label = tk.Label(self.toolbar, text=f"Spoke: {'Found' if self.spoke_interpreter else 'Not Found'}", 
                                   bg=self.theme['toolbar_bg'], fg=self.theme['fg'])
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # Main PanedWindow
        self.main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        # Notebook for editor tabs
        self.notebook = ttk.Notebook(self.main_pane)
        self.main_pane.add(self.notebook, weight=4)

        # Help panel (initially hidden)
        self.help_frame = tk.Frame(self.main_pane, bg=self.theme['sidebar_bg'])
        self.help_panel_visible = False
        # Don't add to main_pane initially

        # Help panel widgets
        help_label = tk.Label(self.help_frame, text="Spoke Help", bg=self.theme['sidebar_bg'], fg=self.theme['sidebar_fg'], font=("Arial", 14, "bold"))
        help_label.pack(pady=5)

        self.help_text = scrolledtext.ScrolledText(self.help_frame, bg=self.theme['sidebar_bg'], fg=self.theme['sidebar_fg'], wrap=tk.WORD, height=20)
        self.help_text.pack(fill=tk.BOTH, expand=True, padx=5)

        # Load help content AFTER creating the widget
        self.load_help_content()

        # Start with a new file
        self.new_file()

    def load_help_content(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            help_path = os.path.join(script_dir, "spokeGuide.txt")
            with open(help_path, "r", encoding="utf-8") as f:
                help_content = f.read()
        except FileNotFoundError:
            help_content = "Help file 'spokeGuide.txt' not found.\nPlease create this file with your Spoke documentation."
        except Exception as e:
            help_content = f"Error loading help file: {e}"
    
        self.help_text.insert("1.0", help_content)
        self.help_text.config(state=tk.DISABLED)
    
    def bind_shortcuts(self):
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-Shift-s>", lambda e: self.save_file_as())
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-y>", lambda e: self.redo())
        self.bind("<Control-x>", lambda e: self.cut())
        self.bind("<Control-c>", lambda e: self.copy())
        self.bind("<Control-v>", lambda e: self.paste())
        self.bind("<Control-f>", lambda e: self.open_find_replace_dialog())
        self.bind("<Control-t>", lambda e: self.switch_theme())
        self.bind("<F5>", lambda e: self.run_program())

    def new_file(self):
        """Create a new file tab"""
        tab = EditorTab(self.notebook, self.theme)
        self.notebook.add(tab, text="Untitled.spk")
        self.notebook.select(tab)
        return tab

    def open_file(self):
        """Open a file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Spoke files", "*.spk"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filename:
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            tab = EditorTab(self.notebook, self.theme, filename=filename, content=content)
            self.notebook.add(tab, text=os.path.basename(filename))
            self.notebook.select(tab)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

    def save_file(self):
        """Save the current file"""
        tab = self.current_tab()
        if not tab:
            return
        
        if tab.filename:
            try:
                content = tab.get_content()
                with open(tab.filename, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Saved", f"File saved: {tab.filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save file as"""
        tab = self.current_tab()
        if not tab:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".spk",
            filetypes=[("Spoke files", "*.spk"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filename:
            return
        
        try:
            content = tab.get_content()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            tab.filename = filename
            self.notebook.tab(tab, text=os.path.basename(filename))
            messagebox.showinfo("Saved", f"File saved as: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")
    
    def close_current_tab(self):
        """Close the current tab"""
        if self.notebook.index("end") > 0:
            current = self.notebook.select()
            if current:
                self.notebook.forget(current)
        
        # If no tabs left, create a new one
        if self.notebook.index("end") == 0:
            self.new_file()

    def current_tab(self):
        """Get the current editor tab"""
        current = self.notebook.select()
        if current:
            return self.notebook.nametowidget(current)
        return None

    def undo(self):
        """Undo in current tab"""
        tab = self.current_tab()
        if tab and hasattr(tab, 'text'):
            try:
                tab.text.edit_undo()
            except tk.TclError:
                pass

    def redo(self):
        """Redo in current tab"""
        tab = self.current_tab()
        if tab and hasattr(tab, 'text'):
            try:
                tab.text.edit_redo()
            except tk.TclError:
                pass

    def cut(self):
        """Cut text in current tab"""
        tab = self.current_tab()
        if tab and hasattr(tab, 'text'):
            try:
                tab.text.event_generate("<<Cut>>")
            except tk.TclError:
                pass

    def copy(self):
        """Copy text in current tab"""
        tab = self.current_tab()
        if tab and hasattr(tab, 'text'):
            try:
                tab.text.event_generate("<<Copy>>")
            except tk.TclError:
                pass

    def paste(self):
        """Paste text in current tab"""
        tab = self.current_tab()
        if tab and hasattr(tab, 'text'):
            try:
                tab.text.event_generate("<<Paste>>")
            except tk.TclError:
                pass

    def open_find_replace_dialog(self):
        """Open find and replace dialog"""
        tab = self.current_tab()
        if not tab:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Find & Replace")
        dialog.geometry("400x150")
        dialog.configure(bg=self.theme['bg'])

        # Find entry
        tk.Label(dialog, text="Find:", bg=self.theme['bg'], fg=self.theme['fg']).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        find_entry = tk.Entry(dialog, bg=self.theme['button_bg'], fg=self.theme['fg'])
        find_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Replace entry
        tk.Label(dialog, text="Replace:", bg=self.theme['bg'], fg=self.theme['fg']).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        replace_entry = tk.Entry(dialog, bg=self.theme['button_bg'], fg=self.theme['fg'])
        replace_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Buttons
        button_frame = tk.Frame(dialog, bg=self.theme['bg'])
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        def find_next():
            find_text = find_entry.get()
            if not find_text:
                return
            
            start_pos = tab.text.index(tk.INSERT)
            pos = tab.text.search(find_text, start_pos, tk.END)
            if pos:
                tab.text.mark_set(tk.INSERT, pos)
                tab.text.tag_remove(tk.SEL, "1.0", tk.END)
                tab.text.tag_add(tk.SEL, pos, f"{pos}+{len(find_text)}c")
                tab.text.see(pos)
            else:
                messagebox.showinfo("Find", "Text not found")

        def replace_current():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            if not find_text:
                return
            
            try:
                if tab.text.get(tk.SEL_FIRST, tk.SEL_LAST) == find_text:
                    tab.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    tab.text.insert(tk.SEL_FIRST, replace_text)
                    find_next()
            except tk.TclError:
                messagebox.showinfo("Replace", "No text selected")

        def replace_all():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            if not find_text:
                return
            
            content = tab.text.get("1.0", tk.END)
            new_content = content.replace(find_text, replace_text)
            count = content.count(find_text)
            
            if count > 0:
                tab.text.delete("1.0", tk.END)
                tab.text.insert("1.0", new_content)
                messagebox.showinfo("Replace All", f"Replaced {count} occurrences")
            else:
                messagebox.showinfo("Replace All", "No occurrences found")

        tk.Button(button_frame, text="Find Next", command=find_next, bg=self.theme['button_bg'], fg=self.theme['fg']).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Replace", command=replace_current, bg=self.theme['button_bg'], fg=self.theme['fg']).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Replace All", command=replace_all, bg=self.theme['button_bg'], fg=self.theme['fg']).pack(side=tk.LEFT, padx=5)

        dialog.columnconfigure(1, weight=1)
        find_entry.focus()

    def run_program(self):
        """Run the current Spoke program"""
        tab = self.current_tab()
        if not tab:
            messagebox.showwarning("Warning", "No file to run")
            return

        if not self.spoke_interpreter:
            messagebox.showerror("Error", "Spoke interpreter not found. Please set the interpreter path.")
            return

        # Save the current file if it has a filename
        if tab.filename:
            self.save_file()
        else:
            # Save as temporary file
            temp_filename = "temp_spoke_program.spk"
            try:
                with open(temp_filename, "w", encoding="utf-8") as f:
                    f.write(tab.get_content())
                tab.filename = temp_filename
            except Exception as e:
                messagebox.showerror("Error", f"Could not save temporary file:\n{e}")
                return

        # Run the program in a separate thread
        def run_spoke():
            try:
                # Create output window
                output_window = tk.Toplevel(self)
                output_window.title("Spoke Output")
                output_window.geometry("600x400")
                output_window.configure(bg=self.theme['bg'])

                output_text = scrolledtext.ScrolledText(output_window, bg=self.theme['bg'], fg=self.theme['fg'], font=("Consolas", 10), state='disabled')
                output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                # Run the spoke program
                process = subprocess.Popen(
                    ["python", "-u", self.spoke_interpreter, tab.filename],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=0,
                    universal_newlines=True
                )

                # Read output line by line
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        output_text.config(state='normal')
                        output_text.insert(tk.END, output)
                        output_text.see(tk.END)
                        output_text.config(state='disabled')
                        output_window.update()
                
                process.wait()
                
                if process.returncode != 0:
                    output_text.insert(tk.END, f"\nProgram exited with code {process.returncode}")
                else:
                    output_text.insert(tk.END, "\nProgram completed successfully")
                
                output_text.see(tk.END)

            except Exception as e:
                messagebox.showerror("Error", f"Could not run program:\n{e}")

        threading.Thread(target=run_spoke, daemon=True).start()

    def set_spoke_interpreter(self):
        """Set the path to the Spoke interpreter"""
        filename = filedialog.askopenfilename(
            title="Select Spoke Interpreter (spoke.py)",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.spoke_interpreter = filename
            self.status_label.config(text="Spoke: Custom Path Set")
            self.config_data["spoke_interpreter"] = filename
            save_config(self.config_data)
            messagebox.showinfo("Success", f"Spoke interpreter set to: {filename}")

    def switch_theme(self):
        """Switch between dark and light themes"""
        if self.current_theme_name == "dark":
            self.current_theme_name = "light"
        else:
            self.current_theme_name = "dark"
        
        self.theme = THEME_PRESETS[self.current_theme_name]
        self.config_data["theme"] = self.current_theme_name
        save_config(self.config_data)
        self.apply_theme()
        
        # Update all open tabs
        for tab_id in self.notebook.tabs():
            tab = self.notebook.nametowidget(tab_id)
            if hasattr(tab, 'theme'):
                tab.theme = self.theme
                tab.create_tags()
                tab.highlight_all()
                tab.text.config(bg=self.theme['bg'], fg=self.theme['fg'], insertbackground=self.theme['fg'])
                tab.line_numbers.config(background=self.theme['line_number_bg'], foreground=self.theme['line_number_fg'])

    def toggle_help_panel(self):
        """Toggle the help panel visibility"""
        if self.help_panel_visible:
            self.main_pane.forget(self.help_frame)
            self.help_panel_visible = False
        else:
            self.main_pane.add(self.help_frame, weight=1)
            self.help_panel_visible = True

    def apply_theme(self):
        """Apply the current theme to all widgets"""
        self.configure(bg=self.theme['bg'])
        
        # Update toolbar
        self.toolbar.config(bg=self.theme['toolbar_bg'])
        for widget in self.toolbar.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(bg=self.theme['button_bg'], fg=self.theme['fg'])
            elif isinstance(widget, tk.Label):
                widget.config(bg=self.theme['toolbar_bg'], fg=self.theme['fg'])
        
        # Update help panel
        self.help_frame.config(bg=self.theme['sidebar_bg'])
        for widget in self.help_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=self.theme['sidebar_bg'], fg=self.theme['sidebar_fg'])
            elif isinstance(widget, scrolledtext.ScrolledText):
                widget.config(bg=self.theme['sidebar_bg'], fg=self.theme['sidebar_fg'])

    def on_close(self):
        """Handle application close"""
        # Save configuration
        save_config(self.config_data)
        self.destroy()

# ------------------------
# Main Application Entry Point
# ------------------------

if __name__ == "__main__":
    app = SpokeEditor()
    app.mainloop()