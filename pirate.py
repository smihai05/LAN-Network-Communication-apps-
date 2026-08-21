import socket
import threading
import tkinter as tk
import ctypes
from ctypes import wintypes

HOST = "0.0.0.0"
PORT = 6767
SERVER_STOP = threading.Event()
server_thread = None
server_socket = None

MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
WM_HOTKEY = 0x0312
HOTKEY_ID = 1


def show_host_menu():
    menu = tk.Toplevel(root)
    menu.title("Change host address")
    menu.geometry("420x190")
    menu.resizable(False, False)
    menu.attributes("-topmost", True)

    tk.Label(
        menu,
        text="Host address",
        font=("Arial", 14, "bold")
    ).pack(pady=(20, 8))

    host_entry = tk.Entry(menu, font=("Arial", 13), width=30)
    host_entry.insert(0, HOST)
    host_entry.pack()
    host_entry.focus_set()

    status = tk.Label(menu, text="", font=("Arial", 10))
    status.pack(pady=6)

    def save_host():
        new_host = host_entry.get().strip()
        if not new_host:
            status.config(text="Enter a host address.", fg="red")
            return

        restart_server(new_host)
        status.config(text=f"Listening on {new_host}:{PORT}", fg="green")
        menu.after(900, menu.destroy)

    tk.Button(
        menu,
        text="Save",
        font=("Arial", 12, "bold"),
        width=12,
        command=save_host
    ).pack(pady=(2, 12))
    menu.bind("<Return>", lambda _event: save_host())


def listen_for_hotkey(hwnd):
    user32 = ctypes.windll.user32
    if not user32.RegisterHotKey(
        hwnd,
        HOTKEY_ID,
        MOD_CONTROL | MOD_SHIFT,
        ord("K")
    ):
        print("Could not register the global Ctrl+Shift+K shortcut.")
        return

    message = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(message), hwnd, 0, 0) > 0:
        if message.message == WM_HOTKEY and message.wParam == HOTKEY_ID:
            root.after(0, show_host_menu)

    user32.UnregisterHotKey(hwnd, HOTKEY_ID)


def show_alert(message):
    window = tk.Toplevel()
    window.title("New message")
    window.geometry("600x300")
    window.resizable(True, True)

    window.attributes("-topmost", True)

    title = tk.Label(
        window,
        text="📩 NEW MESSAGE",
        font=("Arial", 22, "bold")
    )
    title.pack(pady=(25, 10))

    message_label = tk.Label(
        window,
        text=message,
        font=("Arial", 20),
        wraplength=520,
        justify="center"
    )
    message_label.pack(
        expand=True,
        padx=30,
        pady=10
    )

    close_button = tk.Button(
        window,
        text="CLOSE",
        font=("Arial", 14, "bold"),
        width=15,
        height=2,
        command=window.destroy
    )
    close_button.pack(pady=(5, 25))


def start_server():
    global server_socket

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket = server
    server.bind((HOST, PORT))
    server.listen(10)
    server.settimeout(1)

    print(f"Receiver listening on {HOST}:{PORT}")

    while not SERVER_STOP.is_set():
        try:
            connection, address = server.accept()
        except socket.timeout:
            continue
        except OSError:
            break

        try:
            data = connection.recv(4096)

            if data:
                message = data.decode("utf-8")

                print(f"Message received from {address[0]}: {message}")

                root.after(
                    0,
                    show_alert,
                    message
                )

        except Exception as error:
            print("Error:", error)

        finally:
            connection.close()

    server.close()
    server_socket = None


def restart_server(new_host):
    global HOST, server_thread

    SERVER_STOP.set()
    if server_thread and server_thread.is_alive():
        server_thread.join(timeout=2)

    HOST = new_host
    SERVER_STOP.clear()
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()


# Fereastra principală Tkinter
root = tk.Tk()
root.withdraw()

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

root.update_idletasks()
root_hwnd = root.winfo_id()
hotkey_thread = threading.Thread(
    target=listen_for_hotkey,
    args=(root_hwnd,),
    daemon=True
)
hotkey_thread.start()

root.mainloop()
