from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmsgbox
import ttkbootstrap as tb
import subprocess
import threading
import sys
import psutil
from PIL import Image, ImageTk
import pexpect
import wexpect

# Global variables
process = None
output_text = None
process_started = False
emulator_process = None

def Boot_avds():
    global process, output_text, process_started, emulator_process

    if process_started:
        tkmsgbox.showerror("Error", "AVD is already running!")
        return

    if not item_var.get():
        tkmsgbox.showerror("Error", "Please select an Android Model!!!")
        return

    # Command to execute
    if fast_boot_var.get() == 1:
        command = r'C:\Users\subho\Documents\android_sdk\emulator\emulator.exe -avd android_29 -writable-system'
    else:
        command = r'C:\Users\subho\Documents\android_sdk\emulator\emulator.exe -avd android_29 -writable-system -no-snapshot-load'

    # Start the process
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Update the flag
    process_started = True
    print("Process started:", process_started)

    emulator_process = psutil.Process(process.pid)

    # Check if toggle button is checked
    #if show_logs_var.get() == 1 | show_logs_var.get() == 0:

    # Create a new window to display the output
    global output_window
    output_window = Toplevel(root)
    output_window.title("Logs")

    if show_logs_var.get() == 0:
        output_window.withdraw()
        
    # Text widget to display the output
    global output_text
    output_text = Text(output_window, wrap=tk.WORD, width=60, height=20)
    output_text.pack(padx=10, pady=10)

        # Start a thread to continuously read the output
    threading.Thread(target=read_output).start()
 

def read_output():
    # Continuously read the output and update the text widget
    global process_started
    while True:
        line = process.stdout.readline()
        if not line:
            break
        update_output(line)
    process_started = False

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
    global process_started
    global output_window
    if emulator_process:
        kill_process_tree(emulator_process.pid)
        #print("Emulator process terminated successfully.")
        emulator_process = None
        process_started = False
        if output_window:
            output_window.destroy()

    else:
        tkmsgbox.showerror("Error", "Avd Is not running!!!")
def avd_installed_list(x):
    pass

def delete_avd():

    if not item_var.get():
        tkmsgbox.showerror("Error", "Please select an Android Model!!!")
        return

    confirmed = tk.messagebox.askyesno("Confirmation", "Are you sure you want to delete the AVD?")
    if confirmed:
        avd_name = "android_27"
        avdmanager_path = r'C:\Users\subho\\Documents\android_sdk\cmdline-tools\latest\bin\avdmanager.bat'
        try:
            result = subprocess.run([avdmanager_path, "-v", "delete", "avd", "-n", avd_name], capture_output=True, text=True)
            if result.returncode == 0:
                tk.messagebox.showinfo("Success", f"The AVD {avd_name} has been successfully deleted.")
            else:
                error_message = result.stderr.strip() if result.stderr else "Unknown error"
                tk.messagebox.showerror("Error", f"An error occurred: {error_message}. Please make sure that avd is not running!!")
        except FileNotFoundError:
            tk.messagebox.showerror("Error", "avdmanager command not found. Make sure Android SDK is installed and added to the system PATH.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"An unexpected error occurred: {str(e)} . Please make sure avd is not running!!")

    else:
        pass 

def read_values_for_apis(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]
    
def read_values_for_models(filename):
    with open(filename, 'r') as file:
        content = file.read()
        name = content.split('---------\n')
    return name

def run_install_command(output_text):
    # Command to install system image
    command = r'C:\Users\subho\Documents\android_sdk\cmdline-tools\latest\bin\sdkmanager.bat --install "system-images;android-29;google_apis_playstore;x86_64"'
    try:
        # Start the process
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        # Read and update the output in real-time
        for line in process.stdout:
            output_text.insert(tk.END, line.strip() + '\n')
            output_text.see(tk.END)  # Scroll to the end

        # Wait for the process to finish and get the return code
        return_code = process.wait()

        # Print the return code
        print("Return Code:", return_code)

        # If the return code is 0, display a success message and terminate the process
        if return_code == 0:
            tkmsgbox.showinfo("Success", "API downloaded successfully! Now creating AVD...")
            create_avd()
            process.terminate()  # Terminate the process

        else:
            # If the return code is non-zero, display an error message
            tkmsgbox.showerror("Error", f"Command execution failed with return code {return_code}")

    except Exception as e:
        # Display any exceptions as error messages
        tkmsgbox.showerror("Error", str(e))

def Install_avds():
    if not first_combo.get() or not second_combo.get():
        tkmsgbox.showerror("Error", "Please select an Android API And Android Model!!!")
        return
    
    output_text2 = tk.Text(tab2, wrap=tk.WORD)
    output_text2.pack(fill=tk.BOTH, expand=True)

    # Create a thread to execute the command
    install_thread = threading.Thread(target=run_install_command, args=(output_text2,))
    install_thread.start()

def avd_exists(avd_name):
    try:
        # Check if the AVD exists by listing all AVDs
        list_command = r'C:\Users\subho\Documents\android_sdk\cmdline-tools\latest\bin\avdmanager.bat list avd'
        result = subprocess.run(list_command, shell=True, capture_output=True, text=True)
        if avd_name in result.stdout:
            return True
        else:
            return False
    except Exception as e:
        # Display any exceptions as error messages
        tk.messagebox.showerror("Error", f"An unexpected error occurred while checking AVD existence: {str(e)}")
        return False


def run_create_avd_thread(avd_name, output_text):
    command = rf'echo no | C:\Users\subho\Documents\android_sdk\cmdline-tools\latest\bin\avdmanager.bat --verbose create avd --name "android_303" --package "system-images;android-29;google_apis_playstore;x86_64"'

    try:
        # Start the process
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        # Read and update the output in real-time
        for line in process.stdout:
            output_text.insert(tk.END, line.strip() + '\n')
            output_text.see(tk.END)  # Scroll to the end

        # Wait for the process to finish and get the return code
        return_code = process.wait()

        # Print the return code
        print("Return Code:", return_code)

        # If the return code is 0, display a success message and terminate the process
        if return_code == 0:
            tkmsgbox.showinfo("Success", "AVD created successfully! Now Boot the AVD...")
            create_avd()
            process.terminate()  # Terminate the process

        else:
            # If the return code is non-zero, display an error message
            output_text.insert(tk.END, f"Error occurred: {process.stdout.read()}\n")
            tkmsgbox.showerror("Error", f"Command execution failed with return code {return_code}")

    except Exception as e:
        # Display any exceptions as error messages
        tkmsgbox.showerror("Error", str(e))



def create_avd():

    avd_name = "android_303"
    output_text3 = tk.Text(tab2, wrap=tk.WORD)
    output_text3.pack(fill=tk.BOTH, expand=True)

    # Check if the AVD already exists
    if avd_exists(avd_name):
        tkmsgbox.showerror("Error", f"AVD {avd_name} already exists.")
        return

    # Create a thread to execute the command
    create_avd_thread = threading.Thread(target=run_create_avd_thread, args=(avd_name, output_text3))
    create_avd_thread.start()

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
delete_buttoon = tb.Button(tab1, text="Delete", bootstyle="danger", width=10, command=delete_avd)
delete_buttoon.pack(side="left", padx=(10, 40), pady=(0, 450))

# fast Booting Check
global fast_boot_var
fast_boot_var = IntVar(value=1)
fast_boot_var.trace_add("write", on_fast_boot_var_change)
fast_boot_check = tb.Checkbutton(tab1, text="Fast Boot", bootstyle="info, round-toggle", variable=fast_boot_var, onvalue=1, offvalue=0,)
fast_boot_check.pack()
fast_boot_check.place(x=450,y=190)

global show_logs_var
show_logs_var = IntVar(value=1)
show_logs_check = tb.Checkbutton(tab1, text="Show Logs", bootstyle="info, round-toggle", variable=show_logs_var, onvalue=1, offvalue=0,)
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
