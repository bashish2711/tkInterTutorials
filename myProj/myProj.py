#! /usr/bin/env python
"""*********************************************************************
This Editor is copy of Tkeditor.py and we will try to add some more
features like tools>build/Run options with the bugfixes of current
code.
-- ttk Panewindow is added
*********************************************************************"""
try:
    import tkinter as tk
    from tkinter import filedialog
    import tkinter.messagebox as msg
    from tkinter import font
    from tkinter import ttk
    PhotoImage = tk.PhotoImage
except ImportError:
    # Python 2
    import Tkinter as tk
    import tkFileDialog as filedialog
    import tkMessageBox as msg
    import ttk
    import tkFont as font
    from PIL import Image, ImageTk 
    PhotoImage = ImageTk.PhotoImage

import re
import os
from subprocess import Popen, PIPE, STDOUT
from functools import partial
import sys
import traceback
import glob
import configparser as cp
import ntpath

class FindPopup(tk.Toplevel):
    def __init__(self, master):
        try:
            super(FindPopup, self).__init__()
        except TypeError:
            # Python 2
            tk.Toplevel.__init__(self)

        self.master = master

        self.title("Find in file")
        self.center_window()

        self.transient(master)

        self.matches_are_highlighted = False

        self.main_frame = tk.Frame(self, bg="lightgrey")
        self.button_frame = tk.Frame(self.main_frame, bg="lightgrey")

        self.find_label = tk.Label(self.main_frame, text="Find: ", bg="lightgrey", fg="black")
        self.find_entry = tk.Entry(self.main_frame, bg="white", fg="black")
        self.find_button = tk.Button(self.button_frame, text="Find All", bg="lightgrey", fg="black", command=self.find)
        self.next_button = tk.Button(self.button_frame, text="Next", bg="lightgrey", fg="black", command=self.jump_to_next_match)
        self.cancel_button = tk.Button(self.button_frame, text="Cancel", bg="lightgrey", fg="black", command=self.cancel)

        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.find_button.pack(side=tk.LEFT, pady=(0,10), padx=(20,20))
        self.next_button.pack(side=tk.LEFT, pady=(0,10), padx=(15,20))
        self.cancel_button.pack(side=tk.LEFT, pady=(0,10), padx=(15,0))
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.find_label.pack(side=tk.LEFT, fill=tk.X, padx=(20,0))
        self.find_entry.pack(side=tk.LEFT, fill=tk.X, expand=1, padx=(0,20))

        self.find_entry.focus_force()
        self.find_entry.bind("<Return>", self.jump_to_next_match)
        self.find_entry.bind("<KeyRelease>", self.matches_are_not_highlighted)
        self.bind("<Escape>", self.cancel)

        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def find(self, event=None):
        text_to_find = self.find_entry.get()
        if text_to_find and not self.matches_are_highlighted:
            self.master.remove_all_find_tags()
            self.master.highlight_matches(text_to_find)
            self.matches_are_highlighted = True

    def jump_to_next_match(self, event=None):
        text_to_find = self.find_entry.get()
        if text_to_find:
            if not self.matches_are_highlighted:
                self.find()
            self.master.next_match()

    def cancel(self, event=None):
        self.master.remove_all_find_tags()
        self.destroy()

    def matches_are_not_highlighted(self, event):
        key_pressed = event.keysym
        if not key_pressed == "Return":
            self.matches_are_highlighted = False

    def center_window(self):
        master_pos_x = self.master.winfo_x()
        master_pos_y = self.master.winfo_y()

        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()

        my_width = 300
        my_height = 100

        pos_x = (master_pos_x + (master_width // 2)) - (my_width // 2)
        pos_y = (master_pos_y + (master_height // 2)) - (my_height // 2)

        geometry = "{}x{}+{}+{}".format(my_width, my_height, pos_x, pos_y)
        self.geometry(geometry)

class CentralForm(tk.Toplevel):
    def __init__(self,master, my_height=500):
        try:
            super(CentralForm, self).__init__()
        except TypeError:
            # Python 2
            tk.Toplevel.__init__(self)
        self.master = master

        master_pos_x = self.master.winfo_x()
        master_pos_y = self.master.winfo_y()

        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()

        my_width = 300

        pos_x = (master_pos_x + (master_width // 2)) - (my_width // 2)
        pos_y = (master_pos_y + (master_height // 2)) - (my_height // 2)

        geometry = "{}x{}+{}+{}".format(my_width, my_height, pos_x, pos_y)
        self.geometry(geometry)

class AddSectionForm(CentralForm):
    def __init__(self, master):
        try:
            super(AddSectionForm, self).__init__(master)
        except TypeError:
            # Python 2
            CentralForm.__init__(self,master)
        self.title("Add New Section")

        self.main_frame = tk.Frame(self, bg="lightgrey")
        self.name_label = tk.Label(self.main_frame, text="Section Name", bg="lightgrey", fg="black")
        self.name_entry = tk.Entry(self.main_frame, bg="white", fg="black")
        self.submit_button = tk.Button(self.main_frame, text="Create", command=self.create_section)

        self.main_frame.pack(expand=1, fill=tk.BOTH)
        self.name_label.pack(side=tk.TOP, fill=tk.X)
        self.name_entry.pack(side=tk.TOP, fill=tk.X, padx=10)
        self.submit_button.pack(side=tk.TOP, fill=tk.X, pady=(10,0), padx=10)

    def create_section(self):
        section_name = self.name_entry.get()
        if section_name:
            self.master.add_section(section_name)
            self.destroy()
            msg.showinfo("Section Added", "Section " + section_name + " successfully added")
        else:
            msg.showerror("No Name", "Please enter a section name", parent=self)


class AddItemForm(CentralForm):
    def __init__(self,  master):

        my_height = 120

        try:
            super(AddItemForm, self).__init__(master, my_height)
        except TypeError:
            # Python 2
            CentralForm.__init__(self, master, my_height)
        self.master = master
        self.title("Add New Item")

        self.main_frame = tk.Frame(self, bg="lightgrey")
        self.name_label = tk.Label(self.main_frame, text="Item Name", bg="lightgrey", fg="black")
        self.name_entry = tk.Entry(self.main_frame, bg="white", fg="black")
        self.value_label = tk.Label(self.main_frame, text="Item Value", bg="lightgrey", fg="black")
        self.value_entry = tk.Entry(self.main_frame, bg="white", fg="black")
        self.submit_button = tk.Button(self.main_frame, text="Create", command=self.create_item)

        self.main_frame.pack(fill=tk.BOTH, expand=1)
        self.name_label.pack(side=tk.TOP, fill=tk.X)
        self.name_entry.pack(side=tk.TOP, fill=tk.X, padx=10)
        self.value_label.pack(side=tk.TOP, fill=tk.X)
        self.value_entry.pack(side=tk.TOP, fill=tk.X, padx=10)
        self.submit_button.pack(side=tk.TOP, fill=tk.X, pady=(10,0), padx=10)

    def create_item(self):
        item_name = self.name_entry.get()
        item_value = self.value_entry.get()
        if item_name and item_value:
            self.master.add_item(item_name, item_value)
            self.destroy()
            msg.showinfo("Item Added", item_name + " successfully added")
        else:
            msg.showerror("Missing Info", "Please enter a name and value", parent=self)


class IniEditor(tk.Toplevel):
    def __init__(self, master):
        try:
            super(IniEditor, self).__init__()
        except TypeError:
            # Python 2
            tk.Toplevel.__init__(self)

        self.master = master
        self.title("Config File Editor")
        self.geometry("600x600")

        self.active_ini = ""
        self.active_ini_filename = ""
        self.ini_elements = {}

        self.menubar = tk.Menu(self, bg="lightgrey", fg="black")

        self.file_menu = tk.Menu(self.menubar, tearoff=0, bg="lightgrey", fg="black")
        self.file_menu.add_command(label="New", command=self.file_new, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=self.file_open, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.file_save, accelerator="Ctrl+S")

        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.config(menu=self.menubar)

        self.left_frame = tk.Frame(self, width=200, bg="grey")
        self.left_frame.pack_propagate(0)

        self.right_frame = tk.Frame(self, width=400, bg="lightgrey")
        self.right_frame.pack_propagate(0)

        self.file_name_var = tk.StringVar(self)
        self.file_name_label = tk.Label(self, textvar=self.file_name_var, fg="black", bg="white", font=(None, 12))
        self.file_name_label.pack(side=tk.TOP, expand=1, fill=tk.X, anchor="n")

        self.section_select = tk.Listbox(self.left_frame, selectmode=tk.SINGLE)
        self.section_select.configure(exportselection=False)
        self.section_select.pack(expand=1)
        self.section_select.bind("<<ListboxSelect>>", self.display_section_contents)

        self.section_add_button = tk.Button(self.left_frame, text="Add Section", command=self.add_section_form)
        self.section_add_button.pack(pady=(0,20))

        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        self.right_frame.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)

        self.right_frame.bind("<Configure>", self.frame_height)

        self.bind("<Control-n>", self.file_new)
        self.bind("<Control-o>", self.file_open)
        self.bind("<Control-s>", self.file_save)

    def add_section_form(self):
        if not self.active_ini:
            msg.showerror("No File Open", "Please open an ini file first")
            return
        AddSectionForm(self)

    def add_section(self, section_name):
        self.active_ini[section_name] = {}
        self.populate_section_select_box()

    def frame_height(self, event=None):
        new_height = self.winfo_height()
        self.right_frame.configure(height=new_height)

    def file_new(self, event=None):
        ini_file = filedialog.asksaveasfilename(filetypes=[("Configuration file", "*.ini")])

        while ini_file and not ini_file.endswith(".ini"):
            msg.showerror("Wrong Filetype", "Filename must end in .ini")
            ini_file = filedialog.askopenfilename()

        if ini_file:
            self.parse_ini_file(ini_file)

    def file_open(self, event=None):
        ini_file = filedialog.askopenfilename(filetypes=[("Configuration file", "*.ini")])

        while ini_file and not ini_file.endswith(".ini"):
            msg.showerror("Wrong Filetype", "Please select an ini file")
            ini_file = filedialog.askopenfilename()

        if ini_file:
            self.parse_ini_file(ini_file)

    def file_save(self, event=None):
        if not self.active_ini:
            msg.showerror("No File Open", "Please open an ini file first")
            return

        for section in self.active_ini:
            for key in self.active_ini[section]:
                try:
                    self.active_ini[section][key] = self.ini_elements[section][key].get()
                except KeyError:
                    # wasn't changed, no need to save it
                    pass

        with open(self.active_ini_filename, "w") as ini_file:
            self.active_ini.write(ini_file)

        msg.showinfo("Saved", "File Saved Successfully")

    def add_item_form(self):
        AddItemForm(self)

    def add_item(self, item_name, item_value):
        chosen_section = self.section_select.get(self.section_select.curselection())
        self.active_ini[chosen_section][item_name] = item_value
        self.display_section_contents()

    def parse_ini_file(self, ini_file):
        self.active_ini = cp.ConfigParser()
        self.active_ini.read(ini_file)
        self.active_ini_filename = ini_file
        self.populate_section_select_box()

        file_name = ": ".join([ntpath.basename(ini_file), ini_file])
        self.file_name_var.set(file_name)

        self.clear_right_frame()

    def clear_right_frame(self):
        for child in self.right_frame.winfo_children():
            child.destroy()

    def populate_section_select_box(self):
        self.section_select.delete(0, tk.END)

        for index, section in enumerate(self.active_ini.sections()):
            self.section_select.insert(index, section)
            self.ini_elements[section] = {}
        if "DEFAULT" in self.active_ini:
            self.section_select.insert(len(self.active_ini.sections()) + 1, "DEFAULT")
            self.ini_elements["DEFAULT"] = {}

    def display_section_contents(self, event=None):
        if not self.active_ini:
            msg.showerror("No File Open", "Please open an ini file first")
            return

        chosen_section = self.section_select.get(self.section_select.curselection())

        for child in self.right_frame.winfo_children():
            child.pack_forget()

        for key in sorted(self.active_ini[chosen_section]):
            new_label = tk.Label(self.right_frame, text=key, font=(None, 12), bg="black", fg="white")
            new_label.pack(fill=tk.X, side=tk.TOP, pady=(10,0))

            try:
                section_elements = self.ini_elements[chosen_section]
            except KeyError:
                section_elements = {}

            try:
                ini_element = section_elements[key]
            except KeyError:
                value = self.active_ini[chosen_section][key]

                if value.isnumeric():
                    spinbox_default = tk.IntVar(self.right_frame)
                    spinbox_default.set(int(value))
                    ini_element = tk.Spinbox(self.right_frame, from_=0, to=99999, textvariable=spinbox_default, bg="white", fg="black", justify="center")
                else:
                    ini_element = tk.Entry(self.right_frame, bg="white", fg="black", justify="center")
                    ini_element.insert(0, value)

                self.ini_elements[chosen_section][key] = ini_element

            ini_element.pack(fill=tk.X, side=tk.TOP, pady=(0,10))

        save_button = tk.Button(self.right_frame, text="Save Changes", command=self.file_save)
        save_button.pack(side=tk.BOTTOM, pady=(0,20))

        add_button = tk.Button(self.right_frame, text="Add Item", command=self.add_item_form)
        add_button.pack(side=tk.BOTTOM, pady=(0,20))

class Editor(tk.Tk):
    def __init__(self):
        try:
            super(Editor, self).__init__()
        except TypeError:
            # Python 2
            tk.Tk.__init__(self)

        self.FONT = "Ubuntu Mono"
        self.FONT_SIZE = 12
        self.WINDOW_TITLE = "Text Editor with Python Run"
        # self.wm_state('zoomed') // shows maximized window
        self.protocol('WM_DELETE_WINDOW', self.exit_command)
        self.AUTOCOMPLETE_WORDS = [
            "def", "import", "as", "if", "elif", "else", "while",
            "for", "try", "except", "print", "True", "False",
            "self", "None", "return", "with"
        ]
        self.KEYWORDS_1 = ["import", "as", "from", "def", "try", "except", "self"]
        self.KEYWORDS_FLOW = ["if", "else", "elif", "try", "except", "for", "in", "while", "return", "with"]
        self.KEYWORDS_FUNCTIONS = ["print", "list", "dict", "set", "int", "float", "str"]

        self.SPACES_REGEX = re.compile("^\s*")
        self.STRING_REGEX_SINGLE = re.compile("'[^'\r\n]*'")
        self.STRING_REGEX_DOUBLE = re.compile('"[^"\r\n]*"')
        self.NUMBER_REGEX = re.compile(r"\b(?=\(*)\d+\.?\d*(?=\)*\,*)\b")
        self.KEYWORDS_REGEX = re.compile("(?=\(*)(?<![a-z])(None|True|False)(?=\)*\,*)")
        self.SELF_REGEX = re.compile("(?=\(*)(?<![a-z])(self)(?=\)*\,*)")
        self.FUNCTIONS_REGEX = re.compile("(?=\(*)(?<![a-z])(print|list|dict|set|int|str)(?=\()")

        self.REGEX_TO_TAG = {
            self.STRING_REGEX_SINGLE : "string",
            self.STRING_REGEX_DOUBLE : "string",
            self.NUMBER_REGEX : "digit",
            self.KEYWORDS_REGEX : "keywordcaps",
            self.SELF_REGEX : "keyword1",
            self.FUNCTIONS_REGEX : "keywordfunc",
        }

        #we define a color scheme dictionary containg name and color code as key value pair
        self.colorScheme = {
        '1. Default White': '000000.FFFFFF',
        '2. Greygarious Grey':'83406A.D1D4D1',
        '3. Lovely Lavender':'202B4B.E1E1FF' , 
        '4. Aquamarine': '5B8340.D1E7E0',
        '5. Bold Beige': '4B4620.FFF0E1',
        '6. Cobalt Blue':'ffffBB.3333aa',
        '7. Olive Green': 'D1E7E0.5B8340',
        }

        ######################################################################
        #defining icons for compund menu demonstration
        self.newicon = PhotoImage(file='icons/new_file.gif')
        self.openicon = PhotoImage(file='icons/open_file.gif')
        self.saveicon = PhotoImage(file='icons/save.gif')
        self.cuticon = PhotoImage(file='icons/cut.gif')
        self.copyicon = PhotoImage(file='icons/copy.gif')
        self.pasteicon = PhotoImage(file='icons/paste.gif')
        self.undoicon = PhotoImage(file='icons/undo.gif')
        self.redoicon = PhotoImage(file='icons/redo.gif')

        #####################################################################
        # save geometry on exit
        self.ini_file_path = "mapedit.ini"
        try:
            # if the file is there
            # get geometry from file 
            self.ini_file = open(self.ini_file_path,'r')
            self.geometry(self.ini_file.read())
            self.ini_file.close()
        except:
            # if the file is not there, create the file and use default
            # then use default geometry.
            self.ini_file = open(self.ini_file_path, 'w')
            self.ini_file.close()
            self.geometry("640x480+100+200")
        #####################################################################
        # end save geometry on exit

        self.open_file = ""

        self.title(self.WINDOW_TITLE)
        self.menubar = tk.Menu(self, bg="lightgrey", fg="black")

        self.file_menu = tk.Menu(self.menubar, tearoff=0, bg="lightgrey", fg="black")
        self.file_menu.add_command(label="New", compound=tk.LEFT, command=lambda : self.file_new(self), accelerator="Ctrl+N", image=self.newicon)
        self.file_menu.add_command(label="Open", compound=tk.LEFT, command=self.file_open, accelerator="Ctrl+O" , image=self.openicon)
        self.file_menu.add_command(label="Save", compound=tk.LEFT, command=self.file_save, accelerator="Ctrl+S", image=self.saveicon)
        self.file_menu.add_command(label="Save As", compound=tk.LEFT, command=self.file_save_as, accelerator='Shift+Ctrl+S')
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", compound=tk.LEFT, command=self.exit_command, accelerator="Ctrl+W")

        self.edit_menu = tk.Menu(self.menubar, tearoff=0, bg="lightgrey", fg="black")
        self.edit_menu.add_command(label="Cut", compound=tk.LEFT, command=self.edit_cut, accelerator="Ctrl+X", image=self.cuticon)
        self.edit_menu.add_command(label="Paste", compound=tk.LEFT, command=self.edit_paste, accelerator="Ctrl+V", image=self.pasteicon)
        self.edit_menu.add_command(label="Undo", compound=tk.LEFT, command=self.edit_undo, accelerator="Ctrl+Z", image=self.undoicon)
        self.edit_menu.add_command(label="Redo", compound=tk.LEFT, command=self.edit_redo, accelerator="Ctrl+Y", image=self.redoicon)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Find", underline=0, accelerator='Ctrl+F', command=self.show_find_window)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Select All", accelerator='Ctrl+A', underline=7, command=self.select_all)

        #View menu

        self.view_menu = tk.Menu(self.menubar, tearoff=0, bg="lightgrey", fg="black")
        self.showLineNumber = tk.IntVar()
        self.showLineNumber.set(1)
        self.view_menu.add_checkbutton(label="Show Line Number", variable=self.showLineNumber, command=self.show_line_number)
        self.showInfoBar = tk.IntVar()
        self.showInfoBar.set(1)
        self.view_menu.add_checkbutton(label="Show Info Bar at Bottom", variable=self.showInfoBar, command=self.show_info_bar)
        self.highlightCurrentLine = tk.IntVar()
        self.view_menu.add_checkbutton(label="Highlight Current Line", variable=self.highlightCurrentLine, command=self.toggle_highlight)
        self.sidebarToggle = tk.IntVar()
        self.view_menu.add_checkbutton(label="File Explorer",variable=self.sidebarToggle, command=self.show_sidebar_explorer)
        self.themes_menu = tk.Menu(self.view_menu, tearoff=0, bg="lightgrey", fg="black")
        self.view_menu.add_command(label="Ini Editor", command=self.show_ini_editor)


        self.run_menu = tk.Menu(self.menubar, tearoff=0, bg="lightgrey", fg="black")
        self.run_menu.add_command(label="Run", command=self.run, accelerator="Ctrl+B")

        self.about_menu = tk.Menu(self.menubar, tearoff=0, bg="lightgrey", fg="black")
        self.about_menu.add_command(label="About", command=self.about_command)
        # self.log_menu = tk.Menu(self.menubar, tearoff=0, bg="lightgrey", fg="black")
        # self.log_menu.add_command(label="View Log", command=self.show_file_window, accelerator="Ctrl+L")


        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.menubar.add_cascade(label="View", menu=self.view_menu)
        self.menubar.add_cascade(label="Tools", menu=self.run_menu)
        self.menubar.add_cascade(label="About", menu=self.about_menu)
        self.run_menu.entryconfig("Run",state="disabled")

        self.configure(menu=self.menubar)

        #shortcut bar
        self.shortcutbar = tk.Frame(self, height=25)
        self.toolbar = tk.Button(self.shortcutbar, image=self.newicon, text="New", command=self.file_new)
        self.toolbar.pack(side=tk.LEFT)
        self.toolbar = tk.Button(self.shortcutbar, image=self.openicon,  command=self.file_open)
        self.toolbar.pack(side=tk.LEFT)
        self.toolbar = tk.Button(self.shortcutbar, image=self.saveicon,  command=self.file_save)
        self.toolbar.pack(side=tk.LEFT)
        self.toolbar = tk.Button(self.shortcutbar, image=self.cuticon,  command=self.edit_cut)
        self.toolbar.pack(side=tk.LEFT)
        self.toolbar = tk.Button(self.shortcutbar, image=self.pasteicon,  command=self.edit_paste)
        self.toolbar.pack(side=tk.LEFT)
        self.toolbar = tk.Button(self.shortcutbar, image=self.undoicon,  command=self.edit_undo)
        self.toolbar.pack(side=tk.LEFT)
        self.toolbar = tk.Button(self.shortcutbar, image=self.redoicon,  command=self.edit_redo)
        self.toolbar.pack(side=tk.LEFT)

        self.toolbar = tk.Button(self.shortcutbar, image=self.undoicon,  command=self.edit_undo)
        self.toolbar.pack(side=tk.LEFT)
        self.toolbar = tk.Button(self.shortcutbar, image=self.redoicon,  command=self.edit_redo)
        self.toolbar.pack(side=tk.LEFT)


        self.shortcutbar.pack(expand=tk.NO, fill=tk.X)
        # Adjusting Window  in pane
        # the main window is divided into top and bottom sections,
        # and the sidebar is divided into a top and bottom section.
        self.pw = ttk.PanedWindow(orient="horizontal")
        self.sidebar = ttk.PanedWindow(self.pw, orient="vertical")
        self.mainbar = ttk.PanedWindow(self.pw, orient="vertical")
        self.mainbar_pw = ttk.PanedWindow(self.mainbar, orient="horizontal")

        self.main_top_left = tk.Frame(self.mainbar_pw, width=400, height=200, background="white")
        self.main_top_right = tk.Frame(self.mainbar_pw, width=400, height=200, background="white")
        self.main_bottom = tk.Frame(self.mainbar, width=400, height=5, background="black")
        self.sidebar_top = tk.Frame(self.sidebar, width=200, height=400, background="gray")
        # self.sidebar_bottom = tk.Frame(self.sidebar, width=200, height=200, background="white")

        # add the paned window to the root
        self.pw.pack(fill="both", expand=True)

        # add the sidebar and main area to the main paned window
        self.pw.add(self.sidebar)
        self.pw.add(self.mainbar)
        # add the top and bottom to the sidebar
        self.sidebar.add(self.sidebar_top)
        # self.sidebar.add(self.sidebar_bottom)
        self.mainbar.add(self.mainbar_pw)
        self.mainbar_pw.add(self.main_top_left)
        self.mainbar_pw.add(self.main_top_right)
        self.mainbar.add(self.main_bottom)
        self.hide_sidebar_frame = tk.Frame(self.sidebar)
        # self.hide_sidebar_frame.pack(side="top", fill="both", expand=True)

        # self.notebook = ttk.Notebook(self.main_top, height=400)
        # self.tab_trees = {}
        # self.tab = tk.Frame(self.notebook)
        self.main_text = tk.Text(self.main_top_right,wrap='word', bg="white", fg="black", font=(self.FONT, self.FONT_SIZE),undo=True)
        self.scrollbar = tk.Scrollbar(self.main_text, orient="vertical", command=self.scroll_text_and_line_numbers)
        self.main_text.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.main_text.pack(expand=1, fill=tk.BOTH)

        # self.notebook.add(self.tab, text="Editor")
        # self.notebook.pack(fill=tk.BOTH, expand=1)

        # self.main_text = tk.Text(self.main_top, bg="white", fg="black", font=(self.FONT, self.FONT_SIZE),undo=True)
        # self.scrollbar = tk.Scrollbar(self.main_top, orient="vertical", command=self.scroll_text_and_line_numbers)
        # # self.main_text.configure(yscrollcommand=self.scrollbar.set)

        # self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # self.main_text.pack(expand=1, fill=tk.BOTH)

        self.main_text.tag_config("keyword1", foreground="orange")
        self.main_text.tag_config("keywordcaps", foreground="navy")
        self.main_text.tag_config("keywordflow", foreground="purple")
        self.main_text.tag_config("keywordfunc", foreground="darkgrey")
        self.main_text.tag_config("decorator", foreground="khaki")
        self.main_text.tag_config("digit", foreground="red")
        self.main_text.tag_config("string", foreground="green")
        self.main_text.tag_config("findmatch", background="yellow")

        self.main_text.bind("<space>", self.destroy_autocomplete_menu)
        self.main_text.bind("<KeyRelease>", self.on_key_release)
        self.main_text.bind("<Tab>", self.insert_spaces)
        self.main_text.bind("<Escape>", self.destroy_autocomplete_menu)
        self.main_text.bind("<Return>", self.destroy_autocomplete_menu)

        self.main_text.bind("<Control-y>", self.edit_redo)

        self.bind("<Control-s>", self.file_save)
        self.bind("<Control-o>", self.file_open)
        self.bind("<Control-n>", self.file_new)
        self.bind("<Control-w>", self.exit_command)

        self.bind("<Control-a>", self.select_all)
        self.bind("<Control-f>", self.show_find_window)
        self.bind("<Control-v>", self.edit_paste)
        self.bind("<Control-b>", self.run)

        self.main_text.bind("<MouseWheel>", self.scroll_text_and_line_numbers)
        self.main_text.bind("<Button-4>", self.scroll_text_and_line_numbers)
        self.main_text.bind("<Button-5>", self.scroll_text_and_line_numbers)

        # Line Number
        self.line_numbers = tk.Text(self.main_top_left, bg="lightgrey", fg="black", width=5)
        
        self.line_numbers.insert(1.0, "1 \n")
        self.line_numbers.configure(state="disabled")
        self.line_numbers.pack(side=tk.LEFT, fill=tk.BOTH)
        self.line_numbers.bind("<MouseWheel>", self.scroll_text_and_line_numbers)
        self.line_numbers.bind("<Button-4>", self.scroll_text_and_line_numbers)
        self.line_numbers.bind("<Button-5>", self.scroll_text_and_line_numbers)

        # Options related to View>themes

        self.themeChoice= tk.StringVar()
        self.themeChoice.set('1. Default White')
        for k in sorted(self.colorScheme):
            self.themes_menu.add_radiobutton(label=k, variable=self.themeChoice, command=self.theme)

        self.run_out_text = tk.Text(self.main_bottom, bg="black", fg="white", height=5, font=(self.FONT, self.FONT_SIZE))
        self.run_out_scrollbar = tk.Scrollbar(self.main_bottom, orient="vertical", command=self.run_out_text.yview)
        self.run_out_text.configure(yscrollcommand=self.run_out_scrollbar.set)
        # self.run_out_text_hide_btn = tk.Button(self.main_bottom, text="X", command=self.paneHide)
        self.run_out_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Infobar
        self.infobar = tk.Label(self)
        self.infobar.configure(text='Line: 1 | Column:0')
        self.infobar.pack(expand=tk.NO, fill=None, side=tk.RIGHT, anchor='se')

        #######################
        ### Pop up menu on left click
        # set up the pop-up menu
        self.popup_menu = tk.Menu(self.main_text, tearoff=0)
        for i in ('cut', 'copy', 'paste', 'undo', 'redo'):
            cmd = 'self.edit_' + i
            cmd = eval(cmd)
            self.popup_menu.add_command(label=i, compound='left', command=cmd)

        self.popup_menu.add_separator()
        self.popup_menu.add_command(label='Select All', underline=7, command=self.select_all)
        self.main_text.bind('<Button-3>', self.show_popup_menu)
        self.main_text.focus_set()

    def paneHide(self):
        self.withdraw()

    def show_sidebar_explorer(self):
        self.val = self.sidebarToggle.get()
        self.tree = ttk.Treeview(self.sidebar_top,columns=("fullpath", "type", "size"),
        displaycolumns="size", yscrollcommand=lambda f, l: self.autoscroll(self.vsb, f, l),
        xscrollcommand=lambda f, l:self.autoscroll(self.hsb, f, l))
        # style = ttk.Style()
        # style.configure("Treeview", font=(None,11))
        # style.configure("Treeview.Heading", font=(None, 10))
        self.vsb = ttk.Scrollbar(self.sidebar, orient="vertical", command = self.tree.yview)
        self.hsb = ttk.Scrollbar(self.sidebar,orient="horizontal", command = self.tree.xview)

        self.tree.heading("#0", text="Directory", anchor='w')
        self.tree.heading("size", text="Size", anchor='w')
        self.tree.column("size", stretch=0, width=30)

        self.populate_roots(self.tree)
        self.tree.bind('<<TreeviewOpen>>', self.update_tree)
        self.tree.bind('<Double-Button-1>', self.change_dir)

            # Arrange the tree and its scrollbars in the toplevel
        self.hide_sidebar_frame.pack_forget()

        if self.val:
            self.tree.pack(expand=1, fill=tk.BOTH)
            self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
            self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            # self.tree.lower(self.sidebar_top)
            # self.tree.pack_forget()
            self.hide_sidebar_frame.pack(side="top", fill="both", expand=True)
            self.tree.pack_forget()
            self.vsb.pack_forget()
            self.hsb.pack_forget()

        #theme choice
    def theme(self, bgc="white", fgc="black"):
        self.bgc = bgc
        self.fgc = fgc
        self.val = self.themeChoice.get()
        self.clrs = self.colorScheme.get(self.val)
        self.fgc, self.bgc = self.clrs.split('.')
        self.fgc, self.bgc = '#'+self.fgc, '#'+self.bgc
        self.main_text.config(bg=self.bgc, fg=self.fgc)


    def skip_event(self, event=None):
        return "break"

    def scroll_text_and_line_numbers(self, *args):
        try: # from scrollbar
            self.main_text.yview_moveto(args[1])
            self.line_numbers.yview_moveto(args[1])
        except IndexError:
            #from mouse MouseWheel
            event = args[0]
            if event.delta:
                move = -1*(event.delta/120)
            else:
                if event.num == 5:
                    move = 1
                else:
                    move = -1

            self.main_text.yview_scroll(int(move), "units")
            self.line_numbers.yview_scroll(int(move), "units")

        return "break"

    def file_new(self, event=None):
        file_name = filedialog.asksaveasfilename()
        if file_name:
            self.open_file = file_name
            self.main_text.delete(1.0, tk.END)
            self.run_out_text.delete(1.0, tk.END)
            self.title(" - ".join([self.WINDOW_TITLE, self.open_file]))
            self.check_file_for_run_or_build()

    def file_open(self, event=None):
        file_to_open = filedialog.askopenfilename()

        if file_to_open:
            self.open_file = file_to_open
            self.main_text.delete(1.0, tk.END)
            self.run_out_text.delete(1.0, tk.END)

            with open(file_to_open, "r") as file_contents:
                file_lines = file_contents.readlines()
                if len(file_lines) > 0:
                    for index, line in enumerate(file_lines):
                        index = float(index) + 1.0
                        self.main_text.insert(index, line)

        self.title(" - ".join([self.WINDOW_TITLE, self.open_file]))
        self.check_file_for_run_or_build()
        self.tag_all_lines()


    def file_save(self, event=None):
        if not self.open_file:
            new_file_name = filedialog.asksaveasfilename()
            if new_file_name:
                self.open_file = new_file_name

        if self.open_file:
            new_contents = self.main_text.get(1.0, tk.END)
            with open(self.open_file, "w") as open_file:
                open_file.write(new_contents)

    def file_save_as(self,event=None):
        try:
            # Getting a filename to save the file.
            f = tkFileDialog.asksaveasfilename(initialfile='Untitled.txt',defaultextension=".txt",filetypes=[("All Files","*.*"),("Text Documents","*.txt")])
            fh = open(f, 'w')           
            global filename
            filename = f
            textoutput = textPad.get(1.0, END)
            fh.write(textoutput)              
            fh.close()                
            root.title(os.path.basename(f) + " - Tkeditor") # Setting the title of the root widget.
        except:
            pass 

    def exit_command(self, event=None):
        if msg.askokcancel("Quit", "Do you really want to quit?"):
            self.save_geo()
            self.destroy()

    def save_geo(self):
        # save current geometry to the ini file 
        try:
            with open("mapedit.ini", 'w') as ini_file:
                ini_file.write(self.geometry())
                self.infobar['text']="geo sv"
                ini_file.close()
        except:
            infobar['text']="ini file not found"

    def about_command(self):
        label = msg.showinfo("About", "A text Editor with\npython run options\nversion - 0.7")


    def select_all(self, event=None):
        self.main_text.tag_add("sel", 1.0, tk.END)
        return "break"

    def edit_cut(self, event=None):
        self.main_text.event_generate("<<Cut>>")
        return "break"

    def edit_copy():
        self.main_text.event_generate("<<Copy>>")
        return "break"

    def edit_paste(self, event=None):
        self.main_text.event_generate("<<Paste>>")
        self.on_key_release(self)
        self.tag_all_lines()

        return "break"

    def edit_undo(self, event=None):
        self.main_text.event_generate("<<Undo>>")

        return "break"

    def edit_redo(self, event=None):
        self.main_text.event_generate("<<Redo>>")

        return "break"

    #options related to View Menu

    def highlight_line(self,interval=100):
        self.main_text.tag_remove("active_line", 1.0, "end")
        self.main_text.tag_add("active_line", "insert linestart", "insert lineend+1c")
        self.main_text.after(interval, self.toggle_highlight)

    def undo_highlight(self):
        self.main_text.tag_remove("active_line", 1.0, "end")

    def toggle_highlight(self,event=None):
        self.val = self.highlightCurrentLine.get()
        self.undo_highlight() if not self.val else self.highlight_line()

    # options related to view>themes

    def insert_spaces(self, event=None):
        self.main_text.insert(tk.INSERT, "    ")

        return "break"

    def get_menu_coordinates(self):
        bbox = self.bbox(tk.INSERT)
        menu_x = bbox[0] + self.winfo_x() + self.main_text.winfo_x()
        menu_y = bbox[1] + self.winfo_y() + self.main_text.winfo_y() + self.FONT_SIZE + 2

        return (menu_x, menu_y)

    def display_autocomplete_menu(self, event=None):
        current_index = self.main_text.index(tk.INSERT)
        start = self.adjust_floating_index(current_index)

        try:
            currently_typed_word = self.main_text.get(start + " wordstart", tk.INSERT)
        except tk.TclError:
            currently_typed_word = ""

        currently_typed_word = str(currently_typed_word).strip()

        if currently_typed_word:
            self.destroy_autocomplete_menu()

            suggestions = []
            for word in self.AUTOCOMPLETE_WORDS:
                if word.startswith(currently_typed_word) and not currently_typed_word == word:
                    suggestions.append(word)

            if len(suggestions) > 0:
                x, y = self.get_menu_coordinates()
                self.complete_menu = tk.Menu(self, tearoff=0, bg="lightgrey", fg="black")

                for word in suggestions:
                    insert_word_callback = partial(self.insert_word, word=word, part=currently_typed_word, index=current_index)
                    self.complete_menu.add_command(label=word, command=insert_word_callback)

                self.complete_menu.post(x, y)
                self.complete_menu.bind("<Escape>", self.destroy_autocomplete_menu)
                self.main_text.bind("<Down>", self.focus_menu_item)

    def destroy_autocomplete_menu(self, event=None):
        try:
            self.complete_menu.destroy()
            self.main_text.unbind("<Down>")
            self.main_text.unbind("<Escape>")
            self.main_text.unbind("<Return")
            self.main_text.focus_force()
        except AttributeError:
            pass

    def insert_word(self, word, part, index):
        amount_typed = len(part)
        remaining_word = word[amount_typed:]
        remaining_word_offset = " +" + str(len(remaining_word)) + "c"
        self.main_text.insert(index, remaining_word)
        self.main_text.mark_set(tk.INSERT, index + remaining_word_offset)
        self.destroy_autocomplete_menu()
        self.main_text.focus_force()

    def adjust_floating_index(self, number):
        indices = number.split(".")
        x_index = indices[0]
        y_index = indices[1]
        y_as_number = int(y_index)
        y_previous = y_as_number - 1

        return ".".join([x_index, str(y_previous)])

    def focus_menu_item(self, event=None):
        try:
            self.complete_menu.focus_force()
            self.complete_menu.entryconfig(0, state="active")
        except tk.TclError:
            pass

    def tag_all_lines(self):
        final_index = self.main_text.index(tk.END)
        final_line_number = int(final_index.split(".")[0])

        for line_number in range(final_line_number):
            line_to_tag = ".".join([str(line_number), "0"])
            self.tag_keywords(None, line_to_tag)

        self.update_line_numbers()
        # self.scroll_text_and_line_numbers()

    def tag_keywords(self, event=None, current_index=None):
        if not current_index:
            current_index = self.main_text.index(tk.INSERT)
        line_number = current_index.split(".")[0]
        line_beginning = ".".join([line_number, "0"])
        line_text = self.main_text.get(line_beginning, line_beginning + " lineend")
        line_words = line_text.split()
        number_of_spaces = self.number_of_leading_spaces(line_text)
        y_position = number_of_spaces

        for tag in self.main_text.tag_names():
            if tag != "sel":
                self.main_text.tag_remove(tag, line_beginning, line_beginning + " lineend")

        self.add_regex_tags(line_number, line_text)

        for word in line_words:
            stripped_word = word.strip("():,")

            word_start = str(y_position)
            word_end = str(y_position + len(stripped_word))
            start_index = ".".join([line_number, word_start])
            end_index = ".".join([line_number, word_end])

            if stripped_word in self.KEYWORDS_1:
                self.main_text.tag_add("keyword1", start_index, end_index)
            elif stripped_word in self.KEYWORDS_FLOW:
                self.main_text.tag_add("keywordflow", start_index, end_index)
            elif stripped_word.startswith("@"):
                self.main_text.tag_add("decorator", start_index, end_index)

            y_position += len(word) + 1

    def number_of_leading_spaces(self, line):
        spaces = re.search(self.SPACES_REGEX, line)
        if spaces.group(0) is not None:
            number_of_spaces = len(spaces.group(0))
        else:
            number_of_spaces = 0

        return number_of_spaces

    def add_regex_tags(self, line_number, line_text):
        for regex, tag in self.REGEX_TO_TAG.items():
            for match in regex.finditer(line_text):
                start, end = match.span()
                start_index = ".".join([line_number, str(start)])
                end_index = ".".join([line_number, str(end)])
                self.main_text.tag_add(tag, start_index, end_index)

    def on_key_release(self, event):
        if not event.keysym in ("Up", "Down", "Left", "Right", "BackSpace", "Delete", "Escape"):
            self.display_autocomplete_menu()
        self.tag_keywords()
        self.update_line_numbers()

    def update_line_numbers(self):
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete(1.0, tk.END)
        number_of_lines,endcolumn  = self.main_text.index(tk.END).split(".")
        line_number_string = "\n".join(str(no+1) for no in range(int(number_of_lines)))
        self.line_numbers.insert(1.0, line_number_string)
        self.line_numbers.yview_moveto(number_of_lines)
        self.line_numbers.configure(state="disabled")
        currline, curcolumn = self.main_text.index("insert").split('.')
        self.infobar.config(text='Line: %s | Column: %s'  %(currline,curcolumn) )

    def show_find_window(self, event=None):
        FindPopup(self)

    def show_ini_editor(self, event=None):
        IniEditor(self) 

    def highlight_matches(self, text_to_find):
        self.main_text.tag_remove("findmatch", 1.0, tk.END)
        self.match_coordinates = []
        self.current_match = -1

        find_regex = re.compile(text_to_find)
        search_text_lines = self.main_text.get(1.0, tk.END).split("\n")

        for line_number, line in enumerate(search_text_lines):
            line_number += 1
            for match in find_regex.finditer(line):
                start, end = match.span()
                start_index = ".".join([str(line_number), str(start)])
                end_index = ".".join([str(line_number), str(end)])
                self.main_text.tag_add("findmatch", start_index, end_index)
                self.match_coordinates.append((start_index, end_index))

    def next_match(self, event=None):
        try:
            current_target, current_target_end = self.match_coordinates[self.current_match]
            self.main_text.tag_remove("sel", current_target, current_target_end)
            self.main_text.tag_add("findmatch", current_target, current_target_end)
        except IndexError:
            pass

        try:
            self.current_match = self.current_match + 1
            next_target, target_end = self.match_coordinates[self.current_match]
        except IndexError:
            if len(self.match_coordinates) == 0:
                msg.showinfo("No Matches", "No Matches Found")
            else:
                if msg.askyesno("Wrap Search?", "Reached end of file. Continue from the top?"):
                    self.current_match = -1
                    self.next_match()
        else:
            self.main_text.mark_set(tk.INSERT, next_target)
            self.main_text.tag_remove("findmatch", next_target, target_end)
            self.main_text.tag_add("sel", next_target, target_end)
            self.main_text.see(next_target)

    def remove_all_find_tags(self):
        self.main_text.tag_remove("findmatch", 1.0, tk.END)
        self.main_text.tag_remove("sel", 1.0, tk.END)

    def check_file_for_run_or_build(self):
        if self.open_file.endswith(".py"):
            self.run_menu.entryconfig("Run",state="active")


    def run(self,event=None):
        self.file_save(self)
        self.run_out_text.pack(expand=1, fill=tk.BOTH)
        self.run_out_text.delete(1.0, tk.END)
        self.run_out_text.insert(tk.END, "Run Log:\n")
        if not self.open_file:
            self.run_out_text.insert(tk.END, "Please Add/Open File First\n")
        if self.open_file:
            self.cmd = "python " + self.open_file
            try:
                self.process = Popen(self.cmd, shell=True, stdout=PIPE, stderr=STDOUT)
                self.run_out_text.insert(tk.END, "The Command is executed.\n")
                while True:
                    out = self.process.stdout.readline()
                    if out == '' and self.process.poll() is not None:
                        break
                    self.run_out_text.insert(tk.END, out)
                    self.run_out_text.see(tk.END)
            except :
                out = ''.join(traceback.format_exception(*sys.exc_info()))
                self.run_out_text.insert(tk.END, "Run Error\n")
                self.run_out_text.insert(tk.END, out)

    def show_info_bar(self):
        val = self.showInfoBar.get()
        if val:
            self.infobar.pack(expand=tk.NO, fill=None, side=tk.RIGHT, anchor='se')
        elif not val:
            self.infobar.pack_forget()

    def show_line_number(self):
        val = self.showLineNumber.get()
        if val:
            #Info Bar
            self.infobar.configure(text='Line: 1 | Column:0')
        elif not val:
            self.infobar.configure(text=' ')

    def help_box(self,event=None):
        msg.showinfo("Help", "For help email to bashish2711@gmail.com", icon='question')

#########################################################################

    def populate_tree(self,tree, node):
        if tree.set(node, "type") != 'directory':
            return

        path = tree.set(node, "fullpath")
        tree.delete(*tree.get_children(node))

        parent = tree.parent(node)
        special_dirs = [] if parent else glob.glob('.') + glob.glob('..')

        for p in special_dirs + os.listdir(path):
            ptype = None
            p = os.path.join(path, p).replace('\\', '/')
            if os.path.isdir(p): ptype = "directory"
            elif os.path.isfile(p): ptype = "file"

            fname = os.path.split(p)[1]
            id = tree.insert(node, "end", text=fname, values=[p, ptype])

            if ptype == 'directory':
                if fname not in ('.', '..'):
                    tree.insert(id, 0, text="dummy")
                    tree.item(id, text=fname)
            elif ptype == 'file':
                size = os.stat(p).st_size
                tree.set(id, "size", "%d bytes" % size)


    def populate_roots(self,tree):
        dir = os.path.abspath('.').replace('\\', '/')
        node = tree.insert('', 'end', text=dir, values=[dir, "directory"])
        self.populate_tree(tree, node)

    def update_tree(self,event):
        tree = event.widget
        self.populate_tree(tree, tree.focus())

    def change_dir(self,event):
        tree = event.widget
        node = tree.focus()
        if tree.parent(node):
            path = os.path.abspath(tree.set(node, "fullpath"))
            if os.path.isdir(path):
                os.chdir(path)
                tree.delete(tree.get_children(''))
                self.populate_roots(tree)

    def autoscroll(self, sbar, first, last):
        """Hide and show scrollbar as needed."""
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            sbar.pack_forget()
        else:
            sbar.pack(side=tk.RIGHT,fill=tk.Y)
        self.val = self.sidebarToggle.get()
        if self.val:
            sbar.pack_forget()

    def hide_me(event):
        event.widget.pack_forget()

    ###################################
    # PopUp menu
    def show_popup_menu(self, event):
        self.popup_menu.tk_popup(event.x_root, event.y_root)

#########################################################################

if __name__ == "__main__":
    editor = Editor()
    editor.mainloop()