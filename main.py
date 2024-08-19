import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
from PIL import Image, ImageTk

# Connecting to Database
connector = sqlite3.connect('library.db')
cursor = connector.cursor()

connector.execute(
    'CREATE TABLE IF NOT EXISTS Library (BK_NAME TEXT, BK_ID TEXT PRIMARY KEY NOT NULL, AUTHOR_NAME TEXT, BK_STATUS TEXT, CARD_ID TEXT)'
)

# Functions
def issuer_card():
    Cid = sd.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?\t\t\t')
    if not Cid:
        mb.showerror('Issuer ID cannot be zero!', 'Can\'t keep Issuer ID empty, it must have a value')
    else:
        return Cid

def display_records():
    global connector, cursor, tree
    tree.delete(*tree.get_children())
    curr = connector.execute('SELECT * FROM Library')
    data = curr.fetchall()
    for records in data:
        tree.insert('', END, values=records)

def clear_fields():
    # Clear all entry fields and reset the status to 'Availabe'
    
    bk_status.set('Available')
    bk_id.set('')
    bk_name.set('')
    author_name.set('')
    card_id.set('')

    # Enable the Book ID entry and deselect any selected row in the Treeview
    bk_id_entry.config(state='normal')
    try:
        tree.selection_remove(tree.selection()[0])
    except IndexError:
        pass


def clear_and_display():
    clear_fields()
    display_records()

def add_record():
    global connector
    global bk_name, bk_id, author_name, bk_status, card_id

    if bk_status.get() == 'Issued':
        card_id.set(issuer_card())
    else:
        card_id.set('N/A')

    surety = mb.askyesno('Are you sure?', 'Are you sure this is the data you want to enter?\nPlease note that Book ID cannot be changed in the future')

    if surety:
        try:
            connector.execute(
                'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID) VALUES (?, ?, ?, ?, ?)',
                (bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get())
            )
            connector.commit()
            clear_and_display()
            mb.showinfo('Record added', 'The new record was successfully added to your database')
        except sqlite3.IntegrityError:
            mb.showerror('Book ID already in use!', 'The Book ID you are trying to enter is already in the database. Please alter that book\'s record or check any discrepancies on your side.')

def update_record():
    def update():
        global bk_status, bk_name, bk_id, author_name, card_id
        global connector

        if bk_status.get() == 'Issued':
            card_id.set(issuer_card())
        else:
            card_id.set('N/A')

        cursor.execute(
            'UPDATE Library SET BK_NAME=?, BK_STATUS=?, AUTHOR_NAME=?, CARD_ID=? WHERE BK_ID=?',
            (bk_name.get(), bk_status.get(), author_name.get(), card_id.get(), bk_id.get())
        )
        connector.commit()
        clear_and_display()
        edit.destroy()
        bk_id_entry.config(state='normal')
        clear.config(state='normal')

    def view_record():
        if not tree.selection():
            mb.showerror('Error!', 'Please select a book from the database')
            return

        current_item = tree.focus()
        values = tree.item(current_item)
        selection = values["values"]

        bk_id.set(selection[1])
        bk_name.set(selection[0])
        author_name.set(selection[2])
        bk_status.set(selection[3])
        card_id.set(selection[4])

        bk_id_entry.config(state='disable')
        clear.config(state='disable')

    view_record()

    edit = Button(left_frame, text='Update Record', font=btn_font, bg='black', fg='white', activebackground='black', activeforeground='white', width=20, command=update, relief='raised')
    edit.place(x=50, y=375)

# The rest of your code remains unchanged
 
def remove_record():
    if not tree.selection():
        mb.showerror('Error!', 'Please select an item from the database')
        return

    current_item = tree.focus()
    values = tree.item(current_item)
    selection = values["values"]

    cursor.execute('DELETE FROM Library WHERE BK_ID=?', (selection[1],))
    connector.commit()
    tree.delete(current_item)
    mb.showinfo('Done', 'The record you wanted deleted was successfully deleted.')
    clear_and_display()

def delete_inventory():
    if mb.askyesno('Are you sure?', 'Are you sure you want to delete the entire inventory?\n\nThis command cannot be reversed'):
        tree.delete(*tree.get_children())
        cursor.execute('DELETE FROM Library')
        connector.commit()

def change_availability():
    global card_id, tree, connector

    if not tree.selection():
        mb.showerror('Error!', 'Please select a book from the database')
        return

    current_item = tree.focus()
    values = tree.item(current_item)
    BK_id = values['values'][1]
    BK_status = values["values"][3]

    if BK_status == 'Issued':
        surety = mb.askyesno('Is return confirmed?', 'Has the book been returned to you?')
        if surety:
            cursor.execute('UPDATE Library SET BK_STATUS=?, CARD_ID=? WHERE BK_ID=?', ('Available', 'N/A', BK_id))
            connector.commit()
        else:
            mb.showinfo('Cannot be returned', 'The book status cannot be set to Available unless it has been returned')
    else:
        cursor.execute('UPDATE Library SET BK_STATUS=?, CARD_ID=? WHERE BK_ID=?', ('Issued', issuer_card(), BK_id))
        connector.commit()

    clear_and_display()

def login():
    # Dummy login function
    mb.showinfo('Login', 'Login functionality not implemented.')

# Variables
lf_bg = 'Black'  # Left Frame Background Color
rtf_bg = 'grey'  # Right Top Frame Background Color
rbf_bg = 'grey'  # Right Bottom Frame Background Color
btn_hlb_bg = 'black'  # Background color for Head Labels and Buttons

lbl_font = ('Georgia', 13)  # Font for all labels
entry_font = ('Times New Roman', 12)  # Font for all Entry widgets
btn_font = ('Gill Sans MT', 13)

# Initializing the main GUI window
root = Tk()
root.title('PythonGeeks Library Management System')
root.geometry('1010x530')
root.resizable(0, 0)

Label(root, text='LIBRARY MANAGEMENT SYSTEM', font=("Noto Sans CJK TC", 15, 'bold'), bg=btn_hlb_bg, fg='White').pack(side=TOP, fill=X)

# StringVars
bk_status = StringVar()
bk_name = StringVar()
bk_id = StringVar()
author_name = StringVar()
card_id = StringVar()

# Frames
left_frame = Frame(root, bg=lf_bg)
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)

RT_frame = Frame(root, bg=rtf_bg)
RT_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)

RB_frame = Frame(root, bg=rbf_bg)
RB_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)

# Load and set background image for left frame
def set_background_image(frame, image_path):
    def resize_image(event=None):
        img = Image.open(image_path)
        img = img.resize((frame.winfo_width(), frame.winfo_height()), Image.LANCZOS)
        bg_img = ImageTk.PhotoImage(img)
        bg_label.config(image=bg_img)
        bg_label.image = bg_img
    
    bg_label = Label(frame)
    bg_label.place(relwidth=1, relheight=1)
    frame.bind("<Configure>", resize_image)
    resize_image()

# Update this line with the full path to your background image
set_background_image(left_frame, 'C:/Users/Trenise/OneDrive/Desktop/Library Management System - Other/background.jpeg')

# Left Frame
# Left Frame
Label(left_frame, text='Book Name', bg=lf_bg, font=lbl_font, fg='white').place(x=98, y=25)
Entry(left_frame, width=25, font=entry_font, text=bk_name, fg='black', bg='white').place(x=45, y=55)

Label(left_frame, text='Book ID', bg=lf_bg, font=lbl_font, fg='white').place(x=110, y=105)
bk_id_entry = Entry(left_frame, width=25, font=entry_font, text=bk_id, fg='black', bg='white')
bk_id_entry.place(x=45, y=135)

Label(left_frame, text='Author Name', bg=lf_bg, font=lbl_font, fg='white').place(x=90, y=185)
Entry(left_frame, width=25, font=entry_font, text=author_name, fg='black', bg='white').place(x=45, y=215)


# Status dropdown menu in the Left Frame
Label(left_frame, text='Status of the Book', bg=lf_bg, font=lbl_font, fg='white').place(x=75, y=265)

# Configure the OptionMenu with white background and black text
dd = OptionMenu(left_frame, bk_status, *['Available', 'Issued'])
dd.configure(font=entry_font, width=12, fg='black', bg='white', activebackground='white', activeforeground='black')
dd.place(x=75, y=300)


submit = Button(left_frame, text='Add new record', font=btn_font, bg='black', fg='white', activebackground='black', activeforeground='white', width=20, command=add_record, relief='raised')
submit.place(x=50, y=375)

clear = Button(left_frame, text='Clear fields', font=btn_font, bg='black', fg='white', activebackground='black', activeforeground='white', width=20, command=clear_fields, relief='raised')
clear.place(x=50, y=435)

login_btn = Button(left_frame, text='Login', font=btn_font, bg='black', fg='white', activebackground='black', activeforeground='white', width=20, command=login, relief='raised')
login_btn.place(x=50, y=495)

# Right Top Frame
Button(RT_frame, text='Delete book record', font=btn_font, bg='black', fg='white', activebackground='black', activeforeground='white', width=17, command=remove_record, relief='raised').place(x=8, y=30)
Button(RT_frame, text='Delete full inventory', font=btn_font, bg='black', fg='white', activebackground='black', activeforeground='white', width=17, command=delete_inventory, relief='raised').place(x=178, y=30)
Button(RT_frame, text='Update book details', font=btn_font, bg='black', fg='white', activebackground='black', activeforeground='white', width=17, command=update_record, relief='raised').place(x=348, y=30)
Button(RT_frame, text='Change Book Availability', font=btn_font, bg='black', fg='white', activebackground='black', activeforeground='white', width=19, command=change_availability, relief='raised').place(x=518, y=30)

# Right Bottom Frame
Label(RB_frame, text='BOOK INVENTORY', bg=rbf_bg, font=("Noto Sans CJK TC", 15, 'bold'), fg='white').pack(side=TOP, fill=X)

tree = ttk.Treeview(RB_frame, selectmode=BROWSE, columns=('Book Name', 'Book ID', 'Author', 'Status', 'Card ID'), show='headings')
tree.pack(side=LEFT, fill=BOTH, expand=1)
tree.heading('Book Name', text='Book Name', anchor=W)
tree.heading('Book ID', text='Book ID', anchor=W)
tree.heading('Author', text='Author', anchor=W)
tree.heading('Status', text='Status', anchor=W)
tree.heading('Card ID', text='Card ID', anchor=W)
tree.column('Book Name', width=220)
tree.column('Book ID', width=150)
tree.column('Author', width=200)
tree.column('Status', width=150)
tree.column('Card ID', width=150)

scrollbar = Scrollbar(RB_frame, orient=VERTICAL, command=tree.yview)
scrollbar.pack(side=RIGHT, fill=Y)
tree.configure(yscrollcommand=scrollbar.set)

# Available Books Listbox
available_books_label = Label(RB_frame, text='Available Books', bg=rbf_bg, font=lbl_font, fg='white')
available_books_label.pack(pady=10)

available_books_listbox = Listbox(RB_frame, font=entry_font, width=40, height=10, fg='white')
available_books_listbox.pack(side=LEFT, pady=5)

# Scrollbar for Listbox
listbox_scrollbar = Scrollbar(RB_frame, orient=VERTICAL, command=available_books_listbox.yview)
listbox_scrollbar.pack(side=RIGHT, fill=Y)
available_books_listbox.config(yscrollcommand=listbox_scrollbar.set)

# Initialize GUI
clear_and_display()
root.mainloop()
