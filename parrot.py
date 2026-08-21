import socket
import json
import os
import tkinter as tk
from tkinter import messagebox

PORT = 6767
CONFIG_FILE = "config.json"


# -----------------------------
# IP configuration
# -----------------------------

def get_config_path():
    app_data = os.getenv("APPDATA")

    if app_data:
        folder = os.path.join(app_data, "MessageSender")
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, CONFIG_FILE)

    return CONFIG_FILE


def load_ip():
    path = get_config_path()

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("ip", "")
    except:
        return ""


def save_ip(ip):
    path = get_config_path()

    with open(path, "w", encoding="utf-8") as file:
        json.dump({"ip": ip}, file, indent=4)


# -----------------------------
# Edit IP
# -----------------------------

def edit_ip():
    window = tk.Toplevel(root)
    window.title("Edit IP")
    window.geometry("350x160")
    window.resizable(False, False)
    window.grab_set()

    tk.Label(
        window,
        text="PC B IP address:",
        font=("Arial", 11)
    ).pack(pady=(20, 5))

    ip_input = tk.Entry(
        window,
        width=30,
        font=("Arial", 11)
    )
    ip_input.pack()

    ip_input.insert(0, ip_address)

    def save_new_ip():
        new_ip = ip_input.get().strip()

        if not new_ip:
            messagebox.showerror(
                "Error",
                "Enter an IP address.",
                parent=window
            )
            return

        save_ip(new_ip)

        global ip_address
        ip_address = new_ip

        ip_label.config(text=f"PC B: {ip_address}")

        window.destroy()

    tk.Button(
        window,
        text="SAVE",
        width=12,
        command=save_new_ip
    ).pack(pady=15)


# -----------------------------
# Send message
# -----------------------------

def send_message():

    ip = ip_address.strip()
    message = message_input.get("1.0", tk.END).strip()

    if not ip:
        messagebox.showerror(
            "Error",
            "PC B's IP address has not been set."
        )
        return

    if not message:
        messagebox.showerror(
            "Error",
            "Enter a message."
        )
        return

    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.settimeout(5)

        sock.connect((ip, PORT))

        sock.sendall(
            message.encode("utf-8")
        )

        sock.close()

        status_label.config(
            text="✓ Message sent successfully!"
        )

        message_input.delete(
            "1.0",
            tk.END
        )

    except Exception as error:

        status_label.config(
            text="✗ Error sending message"
        )

        messagebox.showerror(
            "Unable to send message",
            str(error)
        )


# -----------------------------
# Interface
# -----------------------------

root = tk.Tk()

root.title("Message Sender")
root.geometry("500x400")
root.resizable(False, False)


# IP

ip_address = load_ip()

ip_frame = tk.Frame(root)
ip_frame.pack(
    fill="x",
    padx=25,
    pady=(25, 10)
)

ip_label = tk.Label(
    ip_frame,
    text=f"PC B: {ip_address if ip_address else 'Not set'}",
    font=("Arial", 11)
)

ip_label.pack(side="left")


edit_button = tk.Button(
    ip_frame,
    text="EDIT IP",
    command=edit_ip
)

edit_button.pack(side="right")


# Message

tk.Label(
    root,
    text="Message:",
    font=("Arial", 11)
).pack(
    anchor="w",
    padx=25,
    pady=(15, 5)
)


message_input = tk.Text(
    root,
    height=8,
    width=52,
    font=("Arial", 11)
)

message_input.pack(
    padx=25
)


# Send

send_button = tk.Button(
    root,
    text="SEND",
    command=send_message,
    width=18,
    height=2,
    font=("Arial", 11, "bold")
)

send_button.pack(
    pady=20
)


# Status

status_label = tk.Label(
    root,
    text="Ready",
    font=("Arial", 10)
)

status_label.pack()


root.mainloop()
