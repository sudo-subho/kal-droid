from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmsgbox
import ttkbootstrap as tb
import subprocess
import threading
import os
import psutil
from PIL import Image, ImageTk

# Global variables
process = None
output_text = None
process_started = False
emulator_process = None

def Boot_avds():
    global process, output_text, process_started, emulator_process

    if not item_var.get():
        tkmsgbox.showerror("Error", "Please select an Android Model!!!")
        return

    # Command to execute
    if fast_boot_var == 1:
        command = r'C:\Users\subho\Documents\android_sdk\emulator\emulator.exe -avd android_29 -writable-system'
    else:
        command = r'C:\Users\subho\Documents\android_sdk\emulator\emulator.exe -avd android_29 -writable-system -no-snapshot-load'

    # Create a new window to display the output
    global output_window
    output_window = Toplevel(root)
    output_window.title("Logs")
    
    # Text widget to display the output
    output_text = Text(output_window, wrap=tk.WORD, width=60, height=20)
    output_text.pack(padx=10, pady=10)

    # Start the process
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Start a thread to continuously read the output
    threading.Thread(target=read_output).start()

    # Update the flag
    process_started = True
    #print("Process started:", process_started)

    emulator_process = psutil.Process(process.pid)

def read_output():
    # Continuously read the output and update the text widget
    while True:
        line = process.stdout.readline()
        if not line:
            break
        update_output(line)

def update_output(line):
    # Update the text widget with the new output
    output_text.insert(tk.END, line)
    output_text.see(tk.END)  # Scroll to the end

def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.terminate()
        psutil.wait_procs(parent.children(), timeout=5)
        parent.terminate()
        parent.wait(5)
    except psutil.NoSuchProcess:
        # Process has already terminated, nothing to do
        pass


def stop_command():
    global emulator_process
    if emulator_process:
        kill_process_tree(emulator_process.pid)
        #print("Emulator process terminated successfully.")
        emulator_process = None
        if output_window:
            output_window.destroy()

    else:
        tkmsgbox.showerror("Error", "Avd Is not running!!!")
def avd_installed_list(x):
    pass

def read_values_for_apis(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]
    
def read_values_for_models(filename):
    with open(filename, 'r') as file:
        content = file.read()
        name = content.split('---------\n')
    return name

def Install_avds():
    if not first_combo.get() or not second_combo.get():
        tkmsgbox.showerror("Error", "Please select an Android API And Android Model!!!")
        return
    
    os.system('cls')
    process = subprocess.Popen([r'C:\Users\subho\Documents\android_sdk\cmdline-tools\latest\bin\sdkmanager.bat', '--list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    global sdk_frame
    sdk_frame = ttk.Frame(tab2)
    sdk_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Display the output in a Text widget
    output_text = tk.Text(sdk_frame, wrap='word', state='disabled')
    output_text.pack(fill='both', expand=True, padx=10, pady=10)

    output_text.config(state='normal')
    output_text.delete('1.0', tk.END)  # Clear previous output
    output_text.insert(tk.END, output.decode('utf-8'))  # Display the output
    output_text.config(state='normal')

    installation_window.destroy()
    

def installation():
    global installation_window
    installation_window = tb.Window(themename="darkly")
    installation_window.title("Install New Avds")
    installation_window.geometry('900x500')
    installation_window.resizable(False, False)

    # 1 Label
    first_label = tb.Label(installation_window, text="Please Select Android Api", font=("Helvetica", 14))
    first_label.pack(pady=20)

    # Create ComboBox for apis
    Android_Api = read_values_for_apis('android_api_list.txt')
    global first_combo
    first_combo = tb.Combobox(installation_window, bootstyle="success", width=400 ,values=Android_Api)
    first_combo.pack(pady=20,padx=20)
    

    # 2 Label
    tb.Label(installation_window, text="Please Select Android Model", font=("Helvetica", 18)).pack(pady=20)

    # Create ComboBox for models
    Android_model = read_values_for_models('android_models_list.txt')
    global second_combo
    second_combo = tb.Combobox(installation_window, bootstyle="success", values=Android_model, width=70)
    second_combo.pack(pady=20,padx=20)

    # Install Button
    tb.Button(installation_window, text="Install", bootstyle="danger", command=Install_avds).pack(pady=20)

def on_fast_boot_var_change(*args):
    if fast_boot_var.get() == 0:
        fast_boot_check.config(text="Cold Boot")
    else:
        fast_boot_check.config(text="Fast Boot")

root = tb.Window(themename="darkly")
root.title("Kal-Droid")
root.geometry('900x700')
root.resizable(False, False)

# Creating Tabs
notebook = ttk.Notebook(root)

tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)

notebook.add(tab1, text="Avds")
notebook.add(tab2, text="Install")
notebook.add(tab3, text="Help")
notebook.pack(expand=True, fill="both")

background_img = ImageTk.PhotoImage(Image.open("bg.png")) 

background_label = Label(tab1, image=background_img)
background_label.place(relwidth=1, relheight=1)


# Tab 1 ----------->

## Bg Img
background_img = ImageTk.PhotoImage(Image.open("bg.png")) 
background_label = Label(tab1, image=background_img)
background_label.place(relwidth=1, relheight=1)

## Label 1
tb.Label(tab1, text="Kal-Droid", bootstyle="success", font=("Helvetica", 28)).pack(pady=10)

# Menu for selecting Avds
avd_menu = tb.Menubutton(tab1, bootstyle="warning", text="Select Avd",width=30)
avd_menu.pack(side="left", padx=(65, 20), pady=(0, 450))

inside_menu = tb.Menu(avd_menu)

item_var = StringVar()
for x in ['android_29', 'secondary', 'danger']:
    inside_menu.add_radiobutton(label=x, variable=item_var, command=lambda x=x: avd_installed_list(x))

avd_menu['menu'] = inside_menu

# Boot Button
boot_buttoon = tb.Button(tab1, text="Boot", bootstyle="success", width=10, command=Boot_avds)
boot_buttoon.pack(side="left", padx=(10, 40), pady=(0, 450))

# Stop Button
stop_buttoon = tb.Button(tab1, text="Stop", bootstyle="danger", width=10, command=stop_command)
stop_buttoon.pack(side="left", padx=(10, 40), pady=(0, 450))

# Delete Button
delete_buttoon = tb.Button(tab1, text="Delete", bootstyle="danger", width=10)
delete_buttoon.pack(side="left", padx=(10, 40), pady=(0, 450))

# fast Booting Check
global fast_boot_var
fast_boot_var = IntVar(value=1)
fast_boot_var.trace_add("write", on_fast_boot_var_change)
fast_boot_check = tb.Checkbutton(tab1, text="Fast Boot", bootstyle="info, round-toggle", variable=fast_boot_var, onvalue=1, offvalue=0,)
fast_boot_check.pack()
fast_boot_check.place(x=450,y=190)

global show_logs_var
show_logs_var = IntVar(value=0)
show_logs_check = tb.Checkbutton(tab1, text="Show Logs", bootstyle="info, round-toggle", variable=fast_boot_var, onvalue=1, offvalue=0,)
show_logs_check.pack()
show_logs_check.place(x=300,y=190)

# Tab 2 ----------->

# Bg Img
background_img2 = ImageTk.PhotoImage(Image.open("bg2.png")) 
background_label2 = Label(tab2, image=background_img2)
background_label2.place(relwidth=1, relheight=1)

## Install Button
tb.Button(tab2, text="Install", bootstyle="success", command=installation).pack(pady=20)

root.mainloop()
