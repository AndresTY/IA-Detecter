import time
import threading
import tkinter as tk
from pynput import keyboard, mouse
import sys
from pywinauto import Desktop
import configparser
import psutil
import os
import subprocess
import platform
import socket

class InputBlocker:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.HOST = config.get("Settings", "host", fallback="")
        self.PORT = int(config.get("Settings", "port", fallback="0"))
        self.LISTENER = config.get("Settings", "listener", fallback="")
        self.password = config.get("Settings", "password", fallback="")
        self.laws = config.get("Settings", "laws", fallback="")
        self.blocking = False
        self.win_open = None
        self.text_block = "BLOCKED"
        self.ia_references = ["chatgpt", "copilot", "bard", "claude", "deepseek", "gemini"]

        self.vscode_ai_extensions = [
            'ai-', '-ai', '.ai', 'ai.',
            'gpt', 'chatgpt', 'gpt3', 'gpt4',
            'copilot', 'github.copilot',
            'intellicode', 'visualstudioexptteam.intellicode',
            'genai', 'codegen', 'code-gen', 'code-gen-ai',
            'codium', 'codeium',
            'codewhisperer', 'whisper',
            'tabnine',
            'kite',
            'llm', 'llama',
            'cody', 'cursor',
            'anthropic', 'claude',
            'openai', 'davinci',
            'completions', 'auto-complete', 'completion',
            'assistant', 'cognitive',
            'machine-learning', 'deep-learning'
        ]

        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)

        self.root = tk.Tk()
        self.root.title("Input Blocker")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.withdraw()

        self.label = tk.Label(self.root, text=self.text_block, font=("Arial", 50), fg="red", bg="black")
        self.label.pack(pady=(100, 50))

        self.password_frame = tk.Frame(self.root, bg="black")
        self.password_frame.pack(pady=20)

        self.password_label = tk.Label(self.password_frame, text="Password:", font=("Arial", 16), fg="white", bg="black")
        self.password_label.grid(row=0, column=0, padx=10)

        self.password_entry = tk.Entry(self.password_frame, font=("Arial", 16), show="*", bg="white", fg="black", width=15)
        self.password_entry.grid(row=0, column=1, padx=10)
        self.password_entry.bind("<Return>", self.check_password)

        self.unlock_button = tk.Button(self.password_frame, text="Unlock", font=("Arial", 14), bg="gray", fg="white",
                                       command=self.check_password)
        self.unlock_button.grid(row=0, column=2, padx=10)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 14), fg="yellow", bg="black")
        self.status_label.pack(pady=20)

        self.frame_grid = tk.Frame(self.root, bg="black")
        self.frame_grid.pack()

        self.label_ext = tk.Label(self.frame_grid, text="", font=("Arial", 25), fg="white", bg="black")
        self.label_ext.grid(row=0, column=0, columnspan=2, pady=(100, 50))
        self.laws_label = tk.Label(self.frame_grid, text=self.laws, font=("Arial", 12), fg="white", bg="black", wraplength=1000)
        self.laws_label.grid(row=1, column=0, columnspan=2, pady=(10, 50))

        self.running = True
        self.beep_active = False

        self.beep_thread = threading.Thread(target=self.continuous_beep, daemon=True)
        self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
        self.listener_unlock = threading.Thread(target=self.unlock_listen, daemon=True)

    def send_notification(self, msg):
        try:
            if not self.HOST or not self.PORT:
                return
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                s.connect((str(self.HOST), int(self.PORT))) 
                s.sendall(msg.encode())
            print(f"Message sent: {msg} - {self.HOST}:{self.PORT}")
        except Exception as e:
            print(f"[Warning] Could not send message '{msg}' to server: {e}")

    def unlock_listen(self):
        port_conn = int(self.PORT)+1
        print(f"Listening on: {self.LISTENER}:{port_conn}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((self.LISTENER, port_conn))
                s.listen()
                print(f"Now listening: {self.LISTENER}:{self.PORT+1}")
                while True:
                    conn, addr = s.accept()
                    with conn:
                        data = conn.recv(1024).decode().strip()
                        print(f"Remote message: {data} from {addr}")
                        if data == "UNLOCK":
                            self.status_label.config(text="Remote unlock received.")
                            self.send_notification("Unblock")
                            if self.win_open:
                                self.win_open.close()
                            time.sleep(1)
                            self.block_input(False)
            except Exception as e:
                print(f"Error in remote verification: {e}")

    def check_password(self, event=None):
        try:
            entered_password = self.password_entry.get()
            if entered_password == self.password:
                self.status_label.config(text="Correct password. Unlocking...")
                self.root.update()
                self.send_notification("Unblock")
                if self.win_open:
                    self.win_open.close()  
                time.sleep(1)
                self.block_input(False)
            else:
                self.status_label.config(text="Incorrect password. Try again.")
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus_set()
        except Exception as e:
            print(f"Error checking password: {e}")

    def start(self):
        try:
            self.keyboard_listener.start()
            self.mouse_listener.start()
            self.beep_thread.start()
            self.detection_thread.start()
            self.listener_unlock.start()
            self.root.mainloop()
        except Exception as e:
            print(f"Error starting the application: {e}")
        finally:
            self.running = False
            time.sleep(0.5)
            sys.exit(0)

    def block_input(self, should_block):
        try:
            self.send_notification("Block")
            if should_block and not self.blocking:
                self.blocking = True
                self.beep_active = True
                self.password_entry.delete(0, tk.END)
                self.root.deiconify()
                self.root.focus_force()
                self.password_entry.focus_set()
                self.root.update()
            elif not should_block and self.blocking:
                self.blocking = False
                self.beep_active = False
                self.text_block = "BLOCKED"
                self.status_label.config(text="")
                self.root.withdraw()
        except Exception as e:
            print(f"Error toggling block state: {e}")

    def detection_loop(self):
        while self.running:
            try:
                time.sleep(2)
                if not self.blocking:
                    self.send_notification("Unblock")
                self.send_notification("Connect")

                if self.running and not self.blocking:
                    windows = Desktop(backend="uia").windows()  # ⚠️ Windows-only
                    for win in windows:
                        if win.window_text():
                            for i in self.ia_references:
                                if i in win.window_text().lower():
                                    self.text_block = f"BLOCKED - {i}"
                                    self.label.config(text=self.text_block)
                                    self.label_ext.config(text=win.window_text())
                                    self.win_open = win
                                    self.root.after(0, lambda: self.block_input(True))
                                    break

                    has_ai_extension, extension_name = self.check_vscode_extensions()
                    if has_ai_extension:
                        self.text_block = f"BLOCKED - VSCode: {extension_name}"
                        self.label.config(text=self.text_block)
                        self.root.after(0, lambda: self.block_input(True))

            except Exception as e:
                time.sleep(1)

    def continuous_beep(self):
        while self.running:
            try:
                if self.beep_active:
                    if platform.system() == "Windows":
                        import winsound
                        winsound.Beep(1000, 300)
                    else:
                        print("\a", end="", flush=True)
                time.sleep(0.5)
            except Exception as e:
                time.sleep(1)

    def on_key_press(self, key):
        return not self.blocking

    def on_mouse_move(self, x, y):
        return not self.blocking

    def on_mouse_click(self, x, y, button, pressed):
        return not self.blocking

    def check_vscode_extensions(self):
        def get_vscode_extensions():
            cmd = "code --list-extensions --show-versions"
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return []
                output = result.stdout.strip()
                return output.split('\n') if output else []
            except Exception:
                return []

        def is_ai_extension(extension_id):
            base_id = extension_id.split('@')[0] if '@' in extension_id else extension_id
            ext_id_lower = base_id.lower()
            return any(keyword in ext_id_lower for keyword in self.vscode_ai_extensions)

        try:
            vscode_processes = [
                proc for proc in psutil.process_iter(['name'])
                if proc.info['name'] and 'code' in proc.info['name'].lower()
            ]
            if not vscode_processes:
                return False, ""

            active = get_vscode_extensions()
            ai_extensions = [ext for ext in active if is_ai_extension(ext)]
            ai_str = "\n".join(f"-> {ext}" for ext in ai_extensions)
            self.label_ext.config(text=ai_str)
            return (True, "AI Extension Detected") if ai_extensions else (False, "")
        except Exception:
            return False, ""

if __name__ == "__main__":
    print("Starting Input Blocker...")
    try:
        blocker = InputBlocker()
        blocker.start()
    except Exception as e:
        print(f"Fatal error: {e}")