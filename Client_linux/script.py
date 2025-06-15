import time
import threading
import tkinter as tk
from pynput import keyboard, mouse
import sys
import configparser
import psutil
import os
import subprocess
import socket

class InputBlocker:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("/usr/share/ia_detecter/config.ini")
        self.HOST = config.get("Configuracion", "host", fallback="")
        self.PORT = int(config.get("Configuracion", "port", fallback=""))
        self.LISTENER = config.get("Configuracion", "listener", fallback="")
        self.password = config.get("Configuracion", "password", fallback="")
        self.laws = config.get("Configuracion", "laws", fallback="")
        self.win_open = None
        self.blocking = False
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
        self.root.title("Bloqueador")
        self.root.attributes("-fullscreen", True)
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.withdraw()

        self.label = tk.Label(self.root, text=self.text_block, font=("Arial", 50), fg="red", bg="black")
        self.label.pack(pady=(100, 50))

        self.password_frame = tk.Frame(self.root, bg="black")
        self.password_frame.pack(pady=20)

        self.password_label = tk.Label(self.password_frame, text="Contraseña: ", font=("Arial", 16), fg="white", bg="black")
        self.password_label.grid(row=0, column=0, padx=10)

        self.password_entry = tk.Entry(self.password_frame, font=("Arial", 16), show="*", bg="white", fg="black", width=15)
        self.password_entry.grid(row=0, column=1, padx=10)
        self.password_entry.bind("<Return>", self.check_password)

        self.unlock_button = tk.Button(self.password_frame, text="Desbloquear", font=("Arial", 14), bg="gray", fg="white",
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
        except Exception:
            pass

    def unlock_listen(self):
        port_conn = int(self.PORT)+1
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((self.LISTENER, port_conn))
                s.listen()
                while True:
                    conn, addr = s.accept()
                    with conn:
                        data = conn.recv(1024).decode().strip()
                        if data == "UNLOCK":
                            self.status_label.config(text="Desbloqueado remotamente.")
                            self.send_notification("Unblock")
                            time.sleep(1)
                            self.block_input(False)
                            subprocess.run(['wmctrl', '-c', self.win_open], stdout=subprocess.PIPE)
            except Exception as e:
                print(f"Error en verificación remota: {e}")

    def check_password(self, event=None):
        entered_password = self.password_entry.get()
        if entered_password == self.password:
            self.status_label.config(text="Contraseña correcta. Desbloqueando...")
            self.root.update()
            self.send_notification("Unblock")
            time.sleep(1)
            self.block_input(False)
            subprocess.run(['wmctrl', '-c', self.win_open], stdout=subprocess.PIPE)
        else:
            self.status_label.config(text="Contraseña incorrecta. Intente nuevamente.")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()

    def start(self):
        try:
            self.keyboard_listener.start()
            self.mouse_listener.start()
            self.beep_thread.start()
            self.detection_thread.start()
            self.listener_unlock.start()
            self.root.mainloop()
        finally:
            self.running = False
            time.sleep(0.5)
            sys.exit(0)

    def block_input(self, should_block):
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

    def detection_loop(self):
        while self.running:
            try:
                time.sleep(2)
                if not self.blocking:
                    self.send_notification("Unblock")
                self.send_notification("Connect")

                if self.running and not self.blocking:
                    titles = self.get_open_windows_titles()
                    for title in titles:
                        for i in self.ia_references:
                            if i in title.lower():
                                self.text_block = f"BLOCKED - {i}"
                                self.label.config(text=self.text_block)
                                self.label_ext.config(text=title)
                                self.win_open = title
                                self.root.after(0, lambda: self.block_input(True))
                                break

                    has_ai_extension, extension_name = self.check_vscode_extensions()
                    if has_ai_extension:
                        self.text_block = f"BLOCKED - VSCode: {extension_name}"
                        self.label.config(text=self.text_block)
                        self.root.after(0, lambda: self.block_input(True))
            except Exception:
                time.sleep(1)

    def continuous_beep(self):
        while self.running:
            if self.beep_active:
                print("\a")  # simple beep
            time.sleep(0.5)

    def on_key_press(self, key):
        return not self.blocking
    def on_mouse_move(self,x,y):
        return not self.blocking
    def on_mouse_click(self,x,y,button,pressed):
        return not self.blocking

    def get_open_windows_titles(self):
        try:
            result = subprocess.run(['wmctrl', '-l'], stdout=subprocess.PIPE, text=True)
            lines = result.stdout.splitlines()
            return [line.split(None, 3)[-1] for line in lines if len(line.split(None, 3)) >= 4]
        except Exception:
            return []

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
            for keyword in self.vscode_ai_extensions:
                if keyword in ext_id_lower:
                    return True
            return False

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
            return (True, "IA Extension Detected") if ai_extensions else (False, "")
        except Exception:
            return False, ""

if __name__ == "__main__":
    print("Iniciando bloqueador de entrada en Linux...")
    try:
        blocker = InputBlocker()
        blocker.start()
    except Exception as e:
        print(f"Error general del programa: {e}")
