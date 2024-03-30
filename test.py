from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmsgbox
import ttkbootstrap as tb
import subprocess
import re
import threading
import psutil
from PIL import Image, ImageTk


# Global variables
process = None
output_text = None
process_started = False
emulator_process = None
installation_window = None
avd_name = None
avd_name_entry = None

def delete_avd():
    if not item_var_menu.get():
        tkmsgbox.showerror("Error", "Please select an Android Model!!!")
        return

    confirmed = tkmsgbox.askyesno("Confirmation", "Are you sure you want to delete the AVD?")
    if confirmed:
        avd_name = item_var_menu.get()
        avdmanager_path = r'C:\Users\subho\\Documents\android_sdk\cmdline-tools\latest\bin\avdmanager.bat'
        try:
            result = subprocess.run([avdmanager_path, "-v", "delete", "avd", "-n", avd_name], capture_output=True, text=True)
            if result.returncode == 0:
                tkmsgbox.showinfo("Success", f"The AVD {avd_name} has been successfully deleted.")
                save_avd_names_to_file('android_name_list.txt')
                update_avd_menu()
            else:
                error_message = result.stderr.strip() if result.stderr else "Unknown error"
                tkmsgbox.showerror("Error", f"An error occurred: {error_message}. Please make sure that avd is not running!!")
        except FileNotFoundError:
            tkmsgbox.showerror("Error", "avdmanager command not found. Make sure Android SDK is installed and added to the system PATH.")
        except Exception as e:
            tkmsgbox.showerror("Error", f"An unexpected error occurred: {str(e)} . Please make sure avd is not running!!")

def Install_avds():

    avd_name = avd_name_entry.get() 

    if not item_var_api.get() or not avd_name_entry.get():
        tkmsgbox.showerror("Error", "Please select an Android API And Android Model!!!")
        return
    
    if avd_exists(avd_name):
        tkmsgbox.showerror("Error", f"AVD {avd_name} already exists.")
        installation_window.destroy()
        return
    
    avd_name = avd_name_entry.get()  # Accessing avd_name_entry here

    output_text2 = tk.Text(tab2, wrap=tk.WORD)
    output_text2.pack(fill=tk.BOTH, expand=True)

    # Create a thread to execute the command
    install_thread = threading.Thread(target=run_install_command, args=(output_text2, avd_name))
    install_thread.start()
    installation_window.destroy()


def run_install_command(output_text, avd_name):
    # Command to install system image
    and_api = item_var_api.get()
    command = rf'C:\Users\subho\Documents\android_sdk\cmdline-tools\latest\bin\sdkmanager.bat --install "{and_api}"'
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
            create_avd(avd_name)  # Call create_avd() after successful installation
            process.terminate()
            #installation_window.destroy()  # Terminate the process

        else:
            # If the return code is non-zero, display an error message
            tkmsgbox.showerror("Error", f"Command execution failed with return code {return_code}")

    except Exception as e:
        # Display any exceptions as error messages
        tkmsgbox.showerror("Error", str(e))


def create_avd(avd_name):
    output_text3 = tk.Text(tab2, wrap=tk.WORD)
    output_text3.pack(fill=tk.BOTH, expand=True)

    # Create a thread to execute the command
    create_avd_thread = threading.Thread(target=run_create_avd_thread, args=(avd_name, output_text3))
    create_avd_thread.start()


def update_avd_menu():
    # Clear the existing menu
    inside_menu.delete(0, tk.END)

    # Read AVD names from the updated file
    with open('android_name_list.txt', 'r') as file:
        avd_names = file.readlines()

    avd_names = [name.strip() for name in avd_names]

    for avd_name in avd_names:
        inside_menu.add_radiobutton(label=avd_name, variable=item_var_menu, command=lambda avd_name=avd_name: avd_installed_list(avd_name))

    avd_menu['menu'] = inside_menu

def save_avd_names_to_file(filename):
    command = r'C:\Users\subho\Documents\android_sdk\cmdline-tools\latest\bin\avdmanager.bat list avd'
    try:
        # Run the command and capture the output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check if the command executed successfully
        if result.returncode == 0:
            #print("Command output:")
            #print(result.stdout)

            # Extract AVD names using regular expression
            avd_names = re.findall(r'Name: (\S+)', result.stdout)

            # Write the AVD names to the file
            with open(filename, 'w') as file:
                for name in avd_names:
                    file.write(name + '\n')
            print(f"AVD names saved to '{filename}' successfully.")
        else:
            print("Error: Failed to retrieve AVD list.")
            if result.stderr:
                print("Error message:", result.stderr)
    except Exception as e:
        print("An error occurred:", str(e))

def Boot_avds():
    avd_to_boot = item_var_menu.get()
    global process, output_text, process_started, emulator_process

    if process_started:
        tkmsgbox.showerror("Error", "AVD is already running!")
        return

    if not item_var_menu.get():
        tkmsgbox.showerror("Error", "Please select an Android Model!!!")
        return

    # Command to execute
    if fast_boot_var.get() == 1:
        command = rf'C:\Users\subho\Documents\android_sdk\emulator\emulator.exe -avd {avd_to_boot} -writable-system'
    else:
        command = rf'C:\Users\subho\Documents\android_sdk\emulator\emulator.exe -avd {avd_to_boot} -writable-system -no-snapshot-load'

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


def read_values_for_apis(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]
    
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
    command = rf'echo no | C:\Users\subho\Documents\android_sdk\cmdline-tools\latest\bin\avdmanager.bat --verbose create avd --name "{avd_name}" --package "system-images;android-29;google_apis_playstore;x86_64"'

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

        if return_code == 0:
            tkmsgbox.showinfo("Success", "AVD created successfully! Now Boot the AVD...")
            process.terminate() # Terminate the process
            save_avd_names_to_file('android_name_list.txt')
            update_avd_menu()

        else:
            output_text.insert(tk.END, f"Error occurred: {process.stdout.read()}\n")
            tkmsgbox.showerror("Error", f"Command execution failed with return code {return_code}")

    except Exception as e:
        tkmsgbox.showerror("Error", str(e))



def avd_installed_list_api(avd_name_api):
    pass

def installation():
    global installation_window

    if installation_window and installation_window.winfo_exists():
        tkmsgbox.showerror("Error", "Installation process is already running.")
        return

    installation_window = tb.Toplevel(root)
    installation_window.title("Install New Avds")
    installation_window.geometry('900x500')
    installation_window.resizable(False, False)

    # 1 Label
    first_label = tb.Label(installation_window, text="Please Select Android Api", font=("Helvetica", 14), bootstyle="warning")
    first_label.pack(pady=20)

    # Create MenuButton for apis
    Android_Api = read_values_for_apis('android_api_list.txt')
    global avd_name
    global first_menu_button
    global item_var_api
    global avd_name_entry

    #avd_name = avd_name_entry.get()
    first_menu_button = tb.Menubutton(installation_window, bootstyle="success", text="Select Android API", width=300)
    first_menu_button.pack(pady=20, padx=20)

    inside_menu = tb.Menu(first_menu_button)
    item_var_api = StringVar()

    for api in Android_Api:
        inside_menu.add_radiobutton(label=api, variable=item_var_api, command=lambda api=api: avd_installed_list(api))

    first_menu_button['menu'] = inside_menu

    

    # 2 Label
    tb.Label(installation_window, text="Enter a name  for your avd!!", font=("Helvetica", 18), bootstyle="warning").pack(pady=20)

    # Create entry for name of avd
    avd_name_entry = tb.Entry(installation_window, bootstyle="secondary", font=("Helvetica", 10), foreground="white", background="grey")
    avd_name_entry.pack(pady=20,padx=20)
    avd_name = avd_name_entry.get()

    # Install Button
    tb.Button(installation_window, text="Install", bootstyle="success", command=Install_avds).pack(pady=20)

def on_closing():
    global installation_window
    if tkmsgbox.askokcancel("Quit", "Are you sure you want to quit?"):
        if installation_window:  # Check if installation_window exists
            installation_window.destroy()  # Close the installation window if it exists
        root.destroy()

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
global item_var_menu
avd_menu = tb.Menubutton(tab1, bootstyle="warning", text="Select Avd",width=30)
avd_menu.pack(side="left", padx=(65, 20), pady=(0, 450))

inside_menu = tb.Menu(avd_menu)

item_var_menu = StringVar()

# Read AVD names from the file
with open('android_name_list.txt', 'r') as file:
    avd_names = file.readlines()

avd_names = [name.strip() for name in avd_names]

for avd_name in avd_names:
    inside_menu.add_radiobutton(label=avd_name, variable=item_var_menu, command=lambda avd_name=avd_name: avd_installed_list(avd_name))

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


#save_avd_names_to_file('android_name_list.txt')
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

