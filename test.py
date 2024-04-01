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
import os
import webbrowser


# Global variables
process = None
output_text = None
process_started_boot = False
process_started_install_api = False
process_started_install_avd = False
emulator_process = None
installation_window = None
avd_name = None
avd_name_entry = None
inside_menu_root = None
item_var_root = None
avd_installed_list_root = None
first_menu_button_root = None
item_var_root = None
first_menu_button_root = None
root_window = None

# Paths of command, tools and images 
base_dir_root = rf'C:\Users\subho\Documents\android_sdk\system-images'
base_dir_sdkmanager = rf'C:\Users\subho\Documents\android_sdk\cmdline-tools\latest\bin\sdkmanager.bat'
base_dir_avdmanager = rf'C:\Users\subho\Documents\android_sdk\cmdline-tools\latest\bin\avdmanager.bat'
base_dir_image = rf'C:\Users\subho\Documents\programming\projects\AndroLab\assets\img'
base_dir_root = rf'C:\Users\subho\Documents\programming\projects\AndroLab\rootAVD\rootAVD.bat'

## General function here ----------------->

def avd_installed_list(x):
    pass

def avd_installed_list_api(avd_name_api):
    pass

def cancel_installing_avd():
    pass

def read_values_for_apis(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

def on_closing():
    global installation_window
    if tkmsgbox.askokcancel("Quit", "Are you sure you want to quit?"):
        if installation_window:  # Check if installation_window exists
            installation_window.destroy() # Close the installation window if it exists
        
        if process_started_boot == True:
            stop_emulator()
        
        if process_started_install_avd or process_started_install_api == True:
            pass
            
        root.destroy()

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


## (Tab-1) Boot, Stop, Delete, fast boot, show logs > functions here ----------------->

def on_fast_boot_var_change(*args): # if fast boot is unchecked the change the text into "cold boot"
    if fast_boot_var.get() == 0:
        fast_boot_check.config(text="Cold Boot")
    else:
        fast_boot_check.config(text="Fast Boot")

def kill_process_tree(pid): # Killing the running avd process and her child (called by stop_emulator())
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.terminate()
        psutil.wait_procs(parent.children(), timeout=5)
        parent.terminate()
        parent.wait(5)
    except psutil.NoSuchProcess:
        pass

def read_output(): # Continuously read the output and update the text widget
    global process_started_boot
    while True:
        line = process.stdout.readline()
        if not line:
            break
        update_output(line)
    process_started_boot = False

def update_output(line): # Update the text widget with the new output
    output_text.insert(tk.END, line)
    output_text.see(tk.END)  # Scroll to the end

def delete_avd(): # deleting the selected avd (delete button)
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

def stop_emulator(): # Stop the running avd (stop button)
    global emulator_process
    global process_started_boot
    global output_window
    if emulator_process:
        kill_process_tree(emulator_process.pid)
        emulator_process = None
        process_started_boot = False
        if output_window:
            output_window.destroy()

    else:
        tkmsgbox.showerror("Error", "Avd Is not running!!!")

def Boot_avds(): # Booting the selected avd 
    avd_to_boot = item_var_menu.get()
    global process, output_text, process_started_boot, emulator_process

    if process_started_boot:
        tkmsgbox.showerror("Error", "AVD is already running!")
        return

    if not item_var_menu.get():
        tkmsgbox.showerror("Error", "Please select an Android Model!!!")
        return

    if fast_boot_var.get() == 1:
        command = rf'C:\Users\subho\Documents\android_sdk\emulator\emulator.exe -avd {avd_to_boot} -writable-system'
    else:
        command = rf'C:\Users\subho\Documents\android_sdk\emulator\emulator.exe -avd {avd_to_boot} -writable-system -no-snapshot-load'

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    process_started_boot = True
    print("Process started:", process_started_boot)

    emulator_process = psutil.Process(process.pid)

    # Create a new window to display the output
    global output_window
    output_window = Toplevel(root)
    output_window.title("Logs")

    # Check if toggle button is checked
    if show_logs_var.get() == 0:
        output_window.withdraw()
        
    # Text widget to display the output
    global output_text
    output_text = Text(output_window, wrap=tk.WORD, width=60, height=20)
    output_text.pack(padx=10, pady=10)

    # Start a thread to continuously read the output
    threading.Thread(target=read_output).start()

## (Tab-2) Install android Api, creating avd > functions here ----------------->
    
def redraw_tab2(): # Re-rendering the tab 2 ()
    for widget in tab2.winfo_children(): # Clear the current contents of tab2
        widget.destroy()

    try:
        background_img2 = Image.open(rf"{base_dir_image}\bg2.png")
        background_img2 = ImageTk.PhotoImage(background_img2)
        background_label2 = Label(tab2, image=background_img2)
        background_label2.image = background_img2 
        background_label2.place(relx=0, rely=0, relwidth=1, relheight=1) 
    except Exception as e:
        print("Error:", e)

    # Install Button
    tb.Button(tab2, text="Install", bootstyle="success", command=installation).pack(pady=20)

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
    global process_started_install_avd
    command = rf'echo no | C:\Users\subho\Documents\android_sdk\cmdline-tools\latest\bin\avdmanager.bat --verbose create avd --name "{avd_name}" --package "system-images;android-29;google_apis_playstore;x86_64"'

    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        process_started_install_avd = True

        for line in process.stdout:
            output_text.insert(tk.END, line.strip() + '\n')
            output_text.see(tk.END)  # Scroll to the end

        return_code = process.wait()

        print("Return Code:", return_code)

        if return_code == 0:
            tkmsgbox.showinfo("Success", "AVD created successfully! Now Boot the AVD...")
            process.terminate()
            process_started_install_avd = False 
            save_avd_names_to_file('android_name_list.txt')
            update_avd_menu()
            installation_window.destroy()
            output_text.delete(1.0, tk.END)
            redraw_tab2()

        else:
            output_text.insert(tk.END, f"Error occurred: {process.stdout.read()}\n")
            tkmsgbox.showerror("Error", f"Command execution failed with return code {return_code}")
            process_started_install_avd = False

    except Exception as e:
        tkmsgbox.showerror("Error", str(e))
        process_started_install_avd = False

def create_avd(avd_name):
    output_text3 = tk.Text(tab2, wrap=tk.WORD)
    output_text3.pack(fill=tk.BOTH, expand=True)

    create_avd_thread = threading.Thread(target=run_create_avd_thread, args=(avd_name, output_text3))
    create_avd_thread.start()

def run_install_api_thread(output_text, avd_name):
    global process_started_install_api

    and_api = item_var_api.get()
    command = rf'echo y | C:\Users\subho\Documents\android_sdk\cmdline-tools\latest\bin\sdkmanager.bat --install "{and_api}"'
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        process_started_install_api = True

        for line in process.stdout:
            output_text.insert(tk.END, line.strip() + '\n')
            output_text.see(tk.END) 

        return_code = process.wait()

        print("Return Code:", return_code)

        if return_code == 0:
            tkmsgbox.showinfo("Success", "API downloaded successfully! Now creating AVD...")
            process_started_install_api = False
            create_avd(avd_name)  # Call create_avd() after successful installation
            process.terminate()  
            output_text.delete(1.0, tk.END)

        else:
            tkmsgbox.showerror("Error", f"Command execution failed with return code {return_code}")
            process_started_install_api = False

    except Exception as e:
        tkmsgbox.showerror("Error", str(e))
        process_started_install_api = False

def Install_avds():
    avd_name = avd_name_entry.get() 

    if not item_var_api.get() or not avd_name_entry.get():
        tkmsgbox.showerror("Error", "Please select an Android API And Android Model!!!")
        return
    
    if avd_exists(avd_name):
        tkmsgbox.showerror("Error", f"AVD {avd_name} already exists.")
        installation_window.destroy()
        return
    
    avd_name = avd_name_entry.get() 

    output_text2 = tk.Text(tab2, wrap=tk.WORD)
    output_text2.pack(fill=tk.BOTH, expand=True)

    install_thread = threading.Thread(target=run_install_api_thread, args=(output_text2, avd_name))
    install_thread.start()
    installation_window.withdraw()

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
    
# Root tab function ------------>
    
def open_website(url):
    webbrowser.open_new(url)

def extract_ramdisk_paths(output):
    # Regular expression pattern to match ramdisk paths
    pattern = r'C:\\.*?\.img'
    # Find all matches of the pattern in the output
    matches = re.findall(pattern, output)
    # Return unique matches
    return list(set(matches))

def run_api_root(command, output_file):
    try:
        # Run the command and capture the output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check if the command executed successfully
        if result.returncode == 0:
            # Extract ramdisk paths from the output
            ramdisk_paths = extract_ramdisk_paths(result.stdout)

            # Write the ramdisk paths to the specified file
            with open(output_file, 'w') as file:
                file.write('\n'.join(ramdisk_paths))
            print(f"Ramdisk paths saved to '{output_file}' successfully.")
        else:
            print("Error: Command execution failed.")
            if result.stderr:
                print("Error message:", result.stderr)
    except Exception as e:
        print("An error occurred:", str(e))

def api_root_list():
    # Define the command to be executed
    command = rf'{base_dir_root} ListAllAVDs'

    # Specify the output file
    output_file = 'api_root.txt'

    # Create a thread to run the command
    command_thread = threading.Thread(target=run_api_root, args=(command, output_file))

    # Start the thread
    command_thread.start()

    # Wait for the thread to finish
    command_thread.join()

def redraw_tab3():
    for widget in tab3.winfo_children():
        widget.destroy()

    try:
        background_img3 = Image.open(rf"{base_dir_image}\bg3.png")
        background_img3 = ImageTk.PhotoImage(background_img3)
        background_label3 = Label(tab3, image=background_img3)
        background_label3.image = background_img3 
        background_label3.place(relx=0, rely=0, relwidth=1, relheight=1)
    except Exception as e:
        print("Error:", e)

    # Install Button
    root_button = tb.Button(tab3, text="Root Avd", bootstyle="danger", command=root_avd)
    root_button.pack(pady=20)

def run_command_for_rooting(command, output_text):
    try:
        # Open a subprocess to run the command
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Read the output line by line
        for line in process.stdout:
            # Append the line to the output text widget
            output_text.insert(tk.END, line)
            output_text.see(tk.END)  # Scroll to the end to show the latest output
            output_text.update()  # Update the display

        # Wait for the process to finish
        process.wait()

        # Notify the user when the command execution is completed
        output_text.insert(tk.END, "\nCommand execution completed.")
        output_text.see(tk.END)  # Scroll to the end
        output_text.update()  # Update the display

    except Exception as e:
        # Display error message if an exception occurs
        output_text.insert(tk.END, f"\nAn error occurred: {str(e)}")
        output_text.see(tk.END)  # Scroll to the end
        output_text.update()  # Update the display
        # Show error message in a message box
        tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")

def run_root_api_threaded(command, output_text):
    # Create a thread to run the command
    command_thread = threading.Thread(target=run_command_for_rooting, args=(command, output_text))
    command_thread.daemon = True  # Set the thread as daemon to stop when the main thread exits
    command_thread.start()

def avd_root_now():

    root_window.destroy()

    if not item_var_root.get():
        tkmsgbox.showerror("Error", "Please select an Android Api for root!!!")
        return
    
    AvdToRoot = item_var_root.get()
    # Define the command to be executed
    command = rf'C:\Users\subho\Documents\programming\projects\AndroLab\rootAVD\rootAVD.bat {AvdToRoot}'


    # Create a frame to hold the text widget
    frame = ttk.Frame(tab3)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create a text widget to display the output
    output_text = tk.Text(frame, wrap=tk.WORD, state=tk.NORMAL)
    output_text.pack(fill=tk.BOTH, expand=True)

    run_root_api_threaded(command, output_text)

    # Create a button to start the command execution
    clear_button = ttk.Button(tab3, text="clear",bootstyle="danger" ,command=redraw_tab3)
    clear_button.pack(pady=10)


def root_avd():
    global root_window
    global api_root
    global first_label_root
    global item_var_root

    api_root_list()

    Android_root = read_values_for_apis('api_root.txt')
    
    root_window = tb.Toplevel(root)
    root_window.title("Root New Avds")
    root_window.geometry('900x500')
    root_window.resizable(False, False)

    # 1 Label
    first_label_root = tb.Label(root_window, text="Please Select Avd Acroding to your Api level, Type and Architecture", font=("Helvetica", 14), bootstyle="warning")
    first_label_root.pack(pady=20)


    # MenuButton
    first_menu_button_root = tb.Menubutton(root_window, bootstyle="success", text="Select Avd To Root", width=50)
    first_menu_button_root.pack(pady=20, padx=20)

    inside_menu_root = tb.Menu(first_menu_button_root)
    item_var_root = StringVar()

    for api_root in Android_root:
        inside_menu_root.add_radiobutton(label=api_root, variable=item_var_root, command=lambda api_root=api_root: avd_installed_list(api_root))

    first_menu_button_root['menu'] = inside_menu_root

    # Root Now Button
    root_button_now = tb.Button(root_window, text="Root Now", bootstyle="danger", command=avd_root_now)
    root_button_now.pack(pady=20)

    # 2 Label
    second_label_root = tb.Label(root_window, text="Please ensure that Avd is running and connected to adb!", font=("Helvetica", 14), bootstyle="warning")
    second_label_root.pack(pady=20)

    # 3 Label
    third_label_root = tb.Label(root_window, text="RootAvd only support few android api Level. So please ensure that Avd is compatible! . Click the link bellow To see Compatibility Chart", font=("Helvetica", 8), bootstyle="warning")
    third_label_root.pack(pady=20)

    # Link Button
    link_button = tb.Button(root_window, text="Link", bootstyle="success", command=lambda: open_website("https://github.com/newbit1/rootAVD/blob/master/CompatibilityChart.md"))
    link_button.pack(pady=20)

#  Rendering Main Gui For The Main App ----------------------------------->

root = tb.Window(themename="darkly")
root.title("Kal-Droid")
root.geometry('900x700')
root.iconbitmap('logo.ico')
#root.resizable(False, False)


# Creating Tabs
notebook = ttk.Notebook(root)

tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
tab4 = ttk.Frame(notebook)

notebook.add(tab1, text="Boot Avds")
notebook.add(tab2, text="Install Avds")
notebook.add(tab3, text="Root Avds")
notebook.add(tab4, text="Support")
notebook.pack(expand=True, fill="both")

# Tab 1 ----------->

## Bg Img
background_img = ImageTk.PhotoImage(Image.open(rf"{base_dir_image}\bg.png")) 
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
stop_buttoon = tb.Button(tab1, text="Stop", bootstyle="danger", width=10, command=stop_emulator)
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
background_img2 = ImageTk.PhotoImage(Image.open(rf"{base_dir_image}\bg2.png")) 
background_label2 = Label(tab2, image=background_img2)
background_label2.place(relwidth=1, relheight=1)

## Install Button
install_button = tb.Button(tab2, text="Install", bootstyle="success", command=installation).pack(pady=20)

# Tab 3 ----------->
background_img3 = ImageTk.PhotoImage(Image.open(rf"{base_dir_image}\bg3.png")) 
background_label3 = Label(tab3, image=background_img3)
background_label3.place(relwidth=1, relheight=1)

## Root Button
root_button = tb.Button(tab3, text="Root Avd", bootstyle="danger", command=root_avd).pack(pady=20)

# Tab 4 ----------->
background_img4 = ImageTk.PhotoImage(Image.open(rf"{base_dir_image}\andro.png")) 
background_label4 = Label(tab4, image=background_img4)
background_label4.place(relwidth=1, relheight=1)

# Description of the App
help_text = tb.Label(tab4, text="Hii i am Subhodeep Baroi aka sudo_subho devloper of kal-droid,", bootstyle="warning", font=("Helvetica", 10))
help_text.pack()
help_text.place(x=230, y=250)

help_text1 = tb.Label(tab4, text="Discover my free, lightweight, and open-source Android emulator! Run the latest Android APIs", bootstyle="warning", font=("Helvetica", 10))
help_text1.pack()
help_text1.place(x=140, y=275)

help_text2 = tb.Label(tab4, text="effortlessly and explore the Android ecosystem with ease. Whether you're a developer testing", bootstyle="warning", font=("Helvetica", 10))
help_text2.pack()
help_text2.place(x=141, y=298)

help_text3 = tb.Label(tab4, text="apps or an enthusiast exploring Android features, our emulator offers a seamless experience.", bootstyle="warning", font=("Helvetica", 10))
help_text3.pack()
help_text3.place(x=140, y=323)

help_text4 = tb.Label(tab4, text="Root your virtual devices and unlock their full potential. Customize and experiment with system-level", bootstyle="warning", font=("Helvetica", 10))
help_text4.pack()
help_text4.place(x=123, y=348)

help_text5 = tb.Label(tab4, text="modifications or test root-reliant apps. We value user feedback;", bootstyle="warning", font=("Helvetica", 10))
help_text5.pack()
help_text5.place(x=240, y=372)

help_text6 = tb.Label(tab4, text="reach out to us on social media for support and suggestions.", bootstyle="warning", font=("Helvetica", 10))
help_text6.pack()
help_text6.place(x=243, y=396)

github = tb.Button(tab4, text="Github", bootstyle="primary", command=lambda: open_website("https://github.com/sudo-subho/kal-droid"))
github.pack()
github.place(x=260, y=450)

twitter = tb.Button(tab4, text="Twitter(X)", bootstyle="danger", command=lambda: open_website("https://twitter.com/sudo_subho"))
twitter.pack()
twitter.place(x=410, y=450)

linkedin = tb.Button(tab4, text="LinkedIn", bootstyle="success", command=lambda: open_website("https://www.linkedin.com/in/subhodeep-baroi-397629252"))
linkedin.pack()
linkedin.place(x=580, y=450)

Email = tb.Button(tab4, text="Email", bootstyle="info", command=lambda: open_website("subhodeepbaroi2@gmail.com"))
Email.pack()
Email.place(x=425, y=500)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

