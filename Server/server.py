import socket
import threading
import tkinter as tk
import configparser
import psutil

def get_ethernet_ip():
    for interface, addresses in psutil.net_if_addrs().items():
        if "Ethernet" in interface and "vEthernet" not in interface:
            for address in addresses:
                if address.family == socket.AF_INET: 
                    return address.address
    return "127.0.0.1"

class ManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Manager")
        self.root.geometry("400x450")
        try:
            self.root.iconbitmap("icon.ico")
        except tk.TclError:
            print("Warning: icon.ico not found. Application will run without an icon.")

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.HOST = self.config.get("Settings", "host", fallback=get_ethernet_ip())
        self.PORT = self.config.get("Settings", "port", fallback="")
        self.PORT_CONN = self.config.get("Settings", "port_conn", fallback="")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._create_admin_frame()
        self._create_machines_frame()

        self.machines = {}
        self.timers = {}   

        self.root.bind("<Configure>", self._update_grid_layout)
        threading.Thread(target=self._socket_server, daemon=True).start()

    def _create_admin_frame(self):
        self.admin_frame = tk.Frame(self.main_frame, borderwidth=2, relief="groove", padx=10, pady=10)
        self.admin_frame.pack(pady=5, fill=tk.X)
        admin_label = tk.Label(self.admin_frame, text="Manager", font=("Arial", 14, "bold"))
        admin_label.pack(pady=2)
        ip_label = tk.Label(self.admin_frame, text=f"IP: {self.HOST}", font=("Arial", 10))
        ip_label.pack(pady=2)

    def _create_machines_frame(self):
        self.machines_frame = tk.Frame(self.main_frame)
        self.machines_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _update_grid_layout(self, event=None):
        width = self.machines_frame.winfo_width()
        rows_cols = 3 if width < 600 else 6 if width < 900 else 9

        for widget in self.machines_frame.winfo_children():
            widget.grid_forget()

        row = col = 0
        for ip, data in self.machines.items():
            data["frame"].grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            col += 1
            if col >= rows_cols:
                col = 0
                row += 1

        for i in range(rows_cols):
            self.machines_frame.grid_columnconfigure(i, weight=1)

    def add_or_update_machine(self, ip, message):
        def send_unlock(target_ip):
            client_port = self.PORT_CONN if self.PORT_CONN else int(self.PORT) + 1
            print(f"Sending UNLOCK to {target_ip.split('\n')[0]}:{client_port}")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect((target_ip.split('\n')[0], client_port))
                    s.sendall(b"UNLOCK")
            except Exception as e:
                print(f"Error sending UNLOCK to {target_ip}: {e}")

        current_status = self.machines.get(ip, {}).get("status")

        if current_status == "Block" and message == "Connect":
            return

        if message == "Connect":
            if ip not in self.machines:
                frame = tk.Frame(self.machines_frame, borderwidth=2, relief="groove", padx=10, pady=10, bg="lightgreen")
                label = tk.Label(frame, text=f"Machine: {ip}", font=("Arial", 12, "bold"), bg="lightgreen")
                label.pack()
                timer_label = tk.Label(frame, text="", font=("Arial", 10), bg="lightgreen")
                timer_label.pack()
                self.machines[ip] = {"frame": frame, "status": "Connect", "timer_label": timer_label}
                frame.pack(pady=5, fill=tk.X)
            else:
                frame = self.machines[ip]["frame"]
                frame.config(bg="lightgreen")
                for widget in frame.winfo_children():
                    widget.destroy()
                label = tk.Label(frame, text=f"Machine: {ip}", font=("Arial", 12, "bold"), bg="lightgreen")
                label.pack()
                timer_label = tk.Label(frame, text="", font=("Arial", 10), bg="lightgreen")
                timer_label.pack()
                self.machines[ip]["status"] = "Connect"
                self.machines[ip]["timer_label"] = timer_label

            if ip in self.timers:
                self.root.after_cancel(self.timers[ip]["after_id"])
            self._start_timer(ip, 2 * 60)

        elif message == "Block":
            if ip in self.machines:
                frame = self.machines[ip]["frame"]
                frame.config(bg="red")
                for widget in frame.winfo_children():
                    widget.destroy()
                label = tk.Label(frame, text=f"Machine: {ip}", font=("Arial", 12, "bold"), fg="white", bg="red")
                label.pack()
                alert_label = tk.Label(frame, text="BLOCKED ALERT!", fg="white", bg="red", font=("Arial", 10, "bold"))
                alert_label.pack()
                unlock_button = tk.Button(frame, text="Unlock", bg="white", command=lambda ip=ip: send_unlock(ip))
                unlock_button.pack(pady=5)
                self.machines[ip]["status"] = "Block"
                if ip in self.timers:
                    self.root.after_cancel(self.timers[ip]["after_id"])
                    del self.timers[ip]
            else:
                frame = tk.Frame(self.machines_frame, borderwidth=2, relief="groove", padx=10, pady=10, bg="red")
                label = tk.Label(frame, text=f"Machine: {ip}", font=("Arial", 12, "bold"), fg="white", bg="red")
                label.pack()
                alert_label = tk.Label(frame, text="BLOCKED ALERT!", fg="white", bg="red", font=("Arial", 10, "bold"))
                alert_label.pack()
                unlock_button = tk.Button(frame, text="Unlock", bg="white", command=lambda ip=ip: send_unlock(ip))
                unlock_button.pack(pady=5)
                frame.pack(pady=5, fill=tk.X)
                self.machines[ip] = {"frame": frame, "status": "Block"}

        elif message == "Unblock":
            if current_status == "Block": 
                frame = self.machines[ip]["frame"]
                frame.config(bg="lightgreen")
                for widget in frame.winfo_children():
                    widget.destroy()
                label = tk.Label(frame, text=f"Machine: {ip}", font=("Arial", 12, "bold"), bg="lightgreen")
                label.pack()
                timer_label = tk.Label(frame, text="", font=("Arial", 10), bg="lightgreen")
                timer_label.pack()
                self.machines[ip]["status"] = "Connect" 
                self.machines[ip]["timer_label"] = timer_label
                self._start_timer(ip, 2 * 60) 

        self._update_grid_layout() 

    def _start_timer(self, ip, remaining_seconds):
        def update_timer():
            nonlocal remaining_seconds
            if ip not in self.machines:
                return

            mins, secs = divmod(remaining_seconds, 60)
            self.machines[ip]["timer_label"].config(text=f"Time Remaining: {mins:02d}:{secs:02d}")
            if remaining_seconds > 0:
                remaining_seconds -= 1
                after_id = self.root.after(1000, update_timer)
                self.timers[ip] = {"after_id": after_id}
            else:
                self._remove_machine_by_timeout(ip)
        update_timer()

    def _remove_machine_by_timeout(self, ip):
        if ip in self.machines:
            self.machines[ip]["frame"].destroy() 
            del self.machines[ip] 
        if ip in self.timers:
            self.root.after_cancel(self.timers[ip]["after_id"]) 
            del self.timers[ip] 
        self._update_grid_layout() 

    def _handle_client(self, conn, addr):
        ip = addr[0]
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            ref = f"{ip}\n{hostname}" 
        except socket.herror:
            hostname = "Unknown"
            ref = f"{ip}\n{hostname}"

        with conn:
            message = conn.recv(1024).decode().strip()
            if message in ["Connect", "Block", "Unblock"]:
                self.root.after(0, self.add_or_update_machine, ref, message)

    def _socket_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((self.HOST, int(self.PORT)))
                s.listen()
                print(f"Server listening on {self.HOST}:{self.PORT}")
                while True:
                    conn, addr = s.accept()
                    threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()
            except Exception as e:
                print(f"Error starting server: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ManagerApp(root)
    root.mainloop()