import os
import getpass
from tkinter import (Tk, END, LabelFrame, Label, StringVar, OptionMenu,
                     IntVar, Checkbutton, Button, Entry, VERTICAL)
from tkcalendar import DateEntry
from tkinter import font as tkFont
from tkinter import ttk
from PIL import ImageTk, Image
import db

"""
https://stackoverflow.com/questions/57772458/how-to-get-a-treeview-columns-to-fit-the-frame-it-is-within
https://stackoverflow.com/questions/4220295/get-tkinter-window-size
https://stackoverflow.com/questions/43681006/python-tkinter-treeview-get-return-parent-name-of-selected-item
https://www.youtube.com/watch?v=tvXFpMGlHPk
https://stackoverflow.com/questions/61280744/tkinter-how-to-adjust-treeview-indentation-size-and-indicator-arrow-image
https://www.javaer101.com/en/article/46648889.html
https://www.youtube.com/watch?v=TdTks2eSx3c
"""

""" BASE VARIABLES """

userPC = getpass.getuser()
df = db.data()
TeamPPL = list(df["Team"].unique())  # my team list
dfUser = None

root = Tk()
root.title("Tasks View")
app_width, app_height = 700, 500  # width and height of tkinter widget
# below the horizontal and vertical offset of the GUI presence
x = y = 50
""" below trial centers the tkinter widget to screen with above settings.
screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenwidth()
x = (screen_width / 2) - (app_width / 2)
y = (screen_height / 2) - (app_height / 2) - abs(
    (app_width - app_height) + ((app_width - app_height) / 2))
"""

default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(family='Segoe UI')

# Treeview
# init vars of your further calc trv col width and min width
col_tk_width = col_min_width = 0
# col width adjustment coefficients and text alignments
# ('Tasks', 'Description', 'Details (Free Text)', 'Duration (Hours)', 'Notes')
wAdj_anc_d = [(0.75, "w"), (0.75, "w"), (0.75, "w"), (0.40, "c"), (0.50, "c")]  # daily
# ('Tasks', 'Description', 'Duration (Hours)')
wAdj_anc_qm = [(1.05, "w"), (1.05, "w"), (1.05, "c")]  # yearly and quarterly

""" FUNCTIONS """

""" SECTION 2 """

def search_clear():
    if ent.index("end") != 0:
        ent.delete(0, END)
        submit_dmq_data()  # show init list if search text is empty
    return

def search_key_pressed(event):
    submit_dmq_data(searchEntry=ent.get())  # search text trigger to update list
    return

def move_up_trv():
    rows = trv.selection()
    for row in rows:
        parent_iid = trv.parent(row)
        trv.move(row, parent_iid, trv.index(row)-1)  # Treeview Rows Move upwards

def move_down_trv():
    rows = trv.selection()
    for row in reversed(rows):
        parent_iid = trv.parent(row)
        trv.move(row, parent_iid, trv.index(row)+1)  # Treeview Rows Move downwards


""" SECTION 3 """

def trv_config_cols(wAdj_anc, trvCols):
    trv.heading('#' + str(0), text="Tasks")
    trv.column('#' + str(0), minwidth=col_min_width, width=int(
        col_tk_width * wAdj_anc[0][0]), stretch=1, anchor=wAdj_anc[0][1])
    for i, col in enumerate(trvCols):
        trv.heading('#' + str(i+1), text=col)
        trv.column('#' + str(i+1), minwidth=col_min_width, width=int(
            col_tk_width * wAdj_anc[i+1][0]), stretch=1, anchor=wAdj_anc[i+1][1])
    return

def trv_resets_and_display_cols(chkBtnsSum):
    if chkBtnsSum > 0:  # if quarter Xor month
        trv["displaycolumns"] = ("Description", "Duration")
        trv_config_cols(wAdj_anc_qm, trv["displaycolumns"])
    else:  # if daily
        trv["displaycolumns"] = ("Description",
                                 "Details (Free Text)", "Duration", "Notes")
        trv_config_cols(wAdj_anc_d, trv["displaycolumns"])

    trv.delete(*trv.get_children())
    return

def team_filtered_grouped(chkBtnQtr, chkBtnMth, *args, **kwargs):
    global dfUser
    if chkBtnQtr > 0:
        dfUserFilter = df[(df["Team"] == team_text.get()) & (
                          df['Period'].dt.quarter == int(
                              (cal.get_date().month-1)//3 + 1))]
    elif chkBtnMth > 0:
        dfUserFilter = df[(df["Team"] == team_text.get()) & (
                          df['Period'].dt.month == int(
                              cal.get_date().month))]
    else:
        dfUserFilter = df[(df["Team"] == team_text.get()) & (
                          df["Period"] == cal.get_date())]
    if 'searchEntry' in kwargs:  # find along all str columns any searched keyword args
        dfUserFilter = dfUserFilter[dfUserFilter.select_dtypes(
                                    include='object').apply(lambda x: x.str.contains(
                                        kwargs.get("searchEntry"),
                                        na=False, case=False)).any(axis=1)]
    else:
        ent.delete(0, END)
    dfUser = dfUserFilter.groupby(['Tasks', 'Description', 'Details (Free Text)',
                                   'Notes'])['Duration (Hours)'].sum() \
                                                                .reset_index() \
                                                                .sort_values('Tasks')
    return dfUser

def submit_dmq_data(*args, **kwargs):  # submit daily, monthly or quarterly data
    chkBtnsSum = int(qvar.get() + mvar.get())
    trv_resets_and_display_cols(chkBtnsSum)
    dfUser = team_filtered_grouped(qvar.get(), mvar.get(), **kwargs)
    distinctTasks = dfUser['Tasks'].unique()
    iid, parentid = 0, 0
    for i in range(len(distinctTasks)):  # my parents
        dfUserTask = dfUser[(dfUser["Tasks"] == distinctTasks[i])]
        trvVals = ("", "", dfUserTask['Duration (Hours)'].sum()
                   ) if chkBtnsSum > 0 else (
                       "", "", dfUserTask['Duration (Hours)'].sum(), "")
        trv.insert(parent='', index='end', iid=iid, text=distinctTasks[i],
                   values=trvVals)
        parentid = iid
        iid += 1
        for taskid, row in enumerate(dfUserTask.values):  # my childrens
            trvVals = (row[1], "", row[4]
                       ) if chkBtnsSum > 0 else (row[1], row[2], row[4], row[3])
            trv.insert(parent=str(parentid), index='end', iid=iid,
                       text=f"{row[0][:3]}_{str(taskid+1)}", values=trvVals)
            iid += 1
    return

def hover_over_row(event):  # highlight row in grey on mouseover
    tree = event.widget
    item = tree.identify_row(event.y)
    tree.tk.call(tree, "tag", "remove", "hover")
    tree.tk.call(tree, "tag", "add", "hover", item)

def openCloseParent(event):  # double click row to open or close nodes
    rowid = trv.identify_row(event.y)
    parent = trv.parent(rowid)
    trv.item(parent, open=not trv.item(parent)['open'])
    root.focus()
    if parent:
        trv.selection_set(parent)
        parentids = trv.get_children()
        idx = parentids.index(parent) + 1
        if idx < len(parentids):
            trv.item(parentids[idx], open=not trv.item(parentids[idx])['open'])


""" NOTEBOOK TABS AND CONTAINERS """

tc = ttk.Notebook(root)  # tkinter menu tabs
t1 = ttk.Frame(tc)
t2 = ttk.Frame(tc)
tc.add(t1, text='Results', state="normal")
tc.pack(expand="yes", fill="both")
tc.add(t2, text='Other', state="hidden")  # insert a second tab for demo purposes

t1.grid_rowconfigure(2, weight=1)  # weight attr is similar to flex:1 in css flexbox
t1.grid_columnconfigure(0, weight=1)

section1 = LabelFrame(t1, text="Team Data")  # tkinter fieldsets
section2 = LabelFrame(t1, text="")
section3 = LabelFrame(t1, text="Team List", bd=2)

section1.grid(row=0, column=0, padx=20, pady=5, sticky="new")
section2.grid(row=1, column=0, padx=20, pady=5, sticky="new")
section3.grid(row=2, column=0, columnspan=4, padx=20, pady=5, sticky="nsew")

""" SECTION 1 - TEAM DATA """

section1.grid_rowconfigure(0, weight=1)
section1.grid_columnconfigure([1, 2], weight=1)

team_label = Label(section1, text='Member', font=('bold', 11))
team_label.grid(row=0, column=0, padx=10, pady=10)
team_text = StringVar()
# below set have assumed for ex. a pc username named fdrandom
# would be the user of F.D. in db Team column and on the tk menu
team_text.set(f"{userPC[0].upper()}.{userPC[1].upper()}.")
# team_text.set to a default value -> team_text.set(TeamPPL[0])
team_dropdown = OptionMenu(section1, team_text, *TeamPPL)  # dropdown menu
# dropdown menu bg and fg colour when user hovers over
team_dropdown['menu'].config(activebackground='#007bff', activeforeground="white")
team_dropdown.grid(row=0, column=1, ipadx=15, padx=6, pady=12, sticky="ew")

# day from tkcalendar
cal = DateEntry(section1, height=10, width=10,
                background='darkblue', foreground='white', borderwidth=2)
cal.grid(row=0, column=2, padx=6, pady=12, sticky="ew")

# Checkbox include or no quarters
qvar = IntVar()
q_chkBtn = Checkbutton(section1, text="All Quarter", variable=qvar)
q_chkBtn.grid(row=0, column=3, padx=6, pady=12, sticky="ew")
# q_chkBtn.select()  # if one wants to have the widget checked

# Checkbox include or no months
mvar = IntVar()
m_chkBtn = Checkbutton(section1, text="All Month", variable=mvar)
m_chkBtn.grid(row=0, column=4, padx=6, pady=12, sticky="ew")
# m_chkBtn.select()  # if one wants to have the widget checked

# submit button
send_button = Button(section1, text='Submit', width=13, bg="#007bff",
                     fg="white", activebackground="#0069d9",
                     activeforeground="white", command=submit_dmq_data)
send_button.grid(row=0, column=5, padx=6, pady=12, sticky="ew")

""" SECTION 2 - SEARCH """

section2.grid_rowconfigure(0, weight=1)
section2.grid_columnconfigure([1, 4, 5], weight=1)

q = StringVar()
lbl = Label(section2, text="Search", font=('bold', 11))
lbl.grid(row=0, column=0, padx=10, pady=12, ipady=1, sticky="ew")
ent = Entry(section2, textvariable=q, width=50,
            highlightbackground="gray75", highlightthickness=1, highlightcolor="gray25")
ent.grid(row=0, column=1, padx=6, pady=12, ipady=1, sticky="ew")
cbtn = Button(section2, text="Clear", width=12, command=search_clear)
cbtn.grid(row=0, column=2, padx=6, pady=12, ipady=1, sticky="ew")
separator = ttk.Separator(section2, orient=VERTICAL)
separator.grid(row=0, column=3, rowspan=1, padx=3, pady=8, sticky="ns")
moveUpbtn = Button(section2, text="Move Up", width=8, border=0,
                   bg="#36454F", fg="white", command=move_up_trv)
moveUpbtn.grid(row=0, column=4, padx=3, pady=12, ipady=0, sticky="ew")
moveDownbtn = Button(section2, text="Move Dn", width=8, border=0,
                     bg="#9fb1be", fg="black", command=move_down_trv)
moveDownbtn.grid(row=0, column=5, padx=3, pady=12, ipady=0, sticky="ew")

ent.bind("<KeyRelease>", search_key_pressed)  # searched entry typing

""" SECTION 3 - TEAM LIST """

""" TREEVIEW STRUCTURE
Quarter Structure
Tasks - Description - Duration
Day Structure
Tasks - Description - Details (Free Text) - Duration - Notes
"""

section3.grid_rowconfigure(0, weight=1)
section3.grid_columnconfigure(0, weight=1)

trv = ttk.Treeview(section3,
                   columns=("Description", "Details (Free Text)", "Duration", "Notes"),
                   height="8")

style = ttk.Style(trv)
style.theme_use('clam')

style.configure('Treeview', indent=15, rowheight=32)

style.configure("Treeview.Heading", background="darkblue", foreground="white",
                bordercolor="#ccc", lightcolor="#ccc", darkcolor="#ccc",
                relief="raised")
style.map("Treeview.Heading", background=[("active", "darkblue")])

# custom indicator images
im_close = Image.open(os.path.join(os.getcwd(), "imgs", "M.png"))
im_close = im_close.resize((15, 15), Image.ANTIALIAS)
img_close = ImageTk.PhotoImage(im_close, name='img_close', master=trv)
im_open = im_close.rotate(90)
img_open = ImageTk.PhotoImage(im_open, name='img_open', master=trv)
im_empty = Image.new('RGBA', (15, 15), '#00000000')
img_empty = ImageTk.PhotoImage(im_empty, name='img_empty', master=trv)

# custom indicator
style.element_create('Treeitem.myindicator', 'image', 'img_close', (
                     'user1', '!user2', 'img_open'), ('user2', 'img_empty'),
                     sticky='w', width=15, padding='9')

# replace Treeitem.indicator by custom one
style.layout('Treeview.Item', [('Treeitem.padding',
             {'sticky': 'nswe',
              'children': [('Treeitem.myindicator', {'side': 'left', 'sticky': ''}),
                           ('Treeitem.image', {'side': 'left', 'sticky': ''}),
                           # ('Treeitem.focus', {'side': 'left', 'sticky': '', \
                           # 'children': [
                           ('Treeitem.text', {'side': 'left', 'sticky': ''})
                           # ]})
                           ]})])

# insert a tag to toggle hovered item
trv.tag_configure('hover', background='#ccced2', foreground="black")

# trv selected item to have a light blue bg and font to bold
style.map("Treeview", background=[("selected", "#b8daff")],
          foreground=[("selected", "black")], font=[("selected", (
              default_font.actual()['family'], 9, 'bold'))])

trv["columns"] = ("Description", "Details (Free Text)", "Duration", "Notes")

# calc what could be your related treeview width and min width
col_tk_width = int(max(
    trv.winfo_width(), trv.winfo_reqwidth()) // (len(trv["columns"])+1))
col_min_width = int(col_tk_width * 0.25)

submit_dmq_data()  # retrieve my tree

trv.grid(row=0, column=0, padx=2, pady=5, ipadx=2, ipady=5, sticky="nwse")

trv.bind('<Double 1>', openCloseParent)
trv.bind("<Motion>", hover_over_row)

# Vertical Scrollbar
yscrollbar = ttk.Scrollbar(section3, orient="vertical", command=trv.yview)
yscrollbar.grid(row=0, column=1, sticky="ns")

# Horizontal Scrollbar
xscrollbar = ttk.Scrollbar(section3, orient="horizontal", command=trv.xview)
xscrollbar.grid(row=1, column=0, sticky="ew")

trv.configure(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)

# root.update()  # should use before geometry func if want to do more responsiveness
root.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")  # w * h plus the offsets
# root.resizable(False, False)  # user can resize or not the height Xor width of gui

root.mainloop()
