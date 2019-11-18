import pyperclip, os, sys
from tkinter import *

if sys.version_info[0] == 2:
    print("Python 3 is required.")
    sys.exit(1)

def submit_action():
    """
    Prepares the file_write function with geeting the user input from the gui
    """
    name = group_add_text.get()
    slot = slot_add_text.get()
    if name == "":
        error_label_type.config(text = "Error")
        error_label.config(text = "Enter a group name")

    if slot == "":
        error_label_type.config(text = "Error")
        error_label.config(text = "Enter a slot name")
    else:
        error_label_type.config(text = "")
        error_label.config(text = "")

    file_write([name, slot])
    slot_add_text.delete(0, END)
    slot_add_text.insert(0, "")
    add_entry_table(name, slot)

def file_write(element):
    """
    Opens the slot.txt (create one if not found) and add a new line with first
    group then slots, seperated with a comma.
    """
    file = open(os.path.join(os.getcwd(), "slots.txt"), "a+")
    file.write("{},{}\n".format(element[0], element[1]))

    file.close()
    return True

def error_message(type, user_text):
    """
    Sets the error type, 0 for information, 1 for Warning, 2 for Error with given
    text, 5 to remove the messages
    """
    if type == 0:
        error_label_type.config(text = "Info", fg = "green")
    if type == 1:
        error_label_type.config(text = "Warning", fg = "#ff9900")
    if type == 2:
        error_label_type.config(text = "Error", fg = "red")
    if type == 5:
        error_label_type.config(text = "", fg = "black")
        error_label.config(text = "")
        return True
    error_label.config(text = user_text)

def add_entry_table(group, slot):
    global c
    group_label = Label(window, text = group)
    slot_label = Label(window, text = slot)
    group_label.grid(row = c, column = 0)
    slot_label.grid(row = c, column = 1)
    c = c + 1

def copy_action():
    f = open(os.getcwd() + "/slots.txt", "r")
    pyperclip.copy('"' + f.read() + '"')
    error_message(0, "Slots copied to clipboard")

if __name__ == "__main__":
    window = Tk()
    window.title("Slotlist input tool")

    error_label_type = Label(window)
    error_label = Label(window)
    group_add_label = Label(window, text = "Group:")
    group_add_text = Entry(window, width = 40)
    slot_add_label = Label(window, text = "Slot:")
    slot_add_text = Entry(window, width = 40)
    submit_button = Button(window, text = "Add entry", command = submit_action)
    copy_button = Button(window, text = "Copy slots", command = copy_action)

    group_add_label.grid(row = 0, column = 0, padx = 5)
    group_add_text.grid(row = 0, column = 1)
    slot_add_label.grid(row = 1, column = 0, padx = 5)
    slot_add_text.grid(row = 1, column = 1)
    submit_button.grid(row = 2, column = 1)
    copy_button.grid(row = 2, column = 0)
    error_label_type.grid(row = 3, column = 0)
    error_label.grid(row = 3, column = 1)

    c = 4
    f = os.remove(os.path.join(os.getcwd(), "slots.txt"))

    window.mainloop()
