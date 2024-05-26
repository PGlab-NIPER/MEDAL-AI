import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import sys
import threading
import queue  # for thread-safe communication

class ConsoleRedirector:
    def __init__(self, log_pane, queue):
        self.log_pane = log_pane
        self.queue = queue

    def write(self, message):
        self.queue.put(message)

    def flush(self):
        pass

class MedalAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MEDAL-AI")
        self.set_window_size(700, 500)
        self.root.configure(bg='#2e2e2e')

        self.current_frame = None
        self.create_welcome_screen()

        # Queue for thread-safe communication
        self.log_queue = queue.Queue()

        # Redirect stdout to log pane
        self.console_redirector = ConsoleRedirector(self.log_pane, self.log_queue)
        sys.stdout = self.console_redirector

    def set_window_size(self, width, height):
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(width, height)
        self.root.maxsize(width, height)

    def create_welcome_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = ttk.Frame(self.root, padding="20 20 20 20", style='TFrame')
        self.current_frame.grid(row=0, column=0, sticky="nsew")

        title_label = ttk.Label(self.current_frame, text="Welcome to MEDAL-AI", font=("Helvetica", 24, 'bold'), style='TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="w")

        model_label = ttk.Label(self.current_frame, text="Select Model:", font=("Helvetica", 14), style='TLabel')
        model_label.grid(row=1, column=0, pady=10, sticky="w")

        self.model_var = tk.StringVar()
        model_options = ["Model 1", "Model 2", "Model 3"]
        model_dropdown = ttk.Combobox(self.current_frame, textvariable=self.model_var, values=model_options, state="readonly", width=30)  # Set the width here
        model_dropdown.grid(row=2, column=0, pady=10, padx=5, sticky="w")

        load_button = ttk.Button(self.current_frame, text="Load", command=self.load_model, style='TButton')
        load_button.grid(row=2, column=1, pady=10, padx=5, sticky="e")

        unload_button = ttk.Button(self.current_frame, text="Unload", command=self.unload_model, style='TButton')
        unload_button.grid(row=2, column=2, pady=10, padx=5, sticky="e")

        self.log_pane = scrolledtext.ScrolledText(self.current_frame, wrap=tk.WORD, width=70, height=10, state='disabled', bg="#1e1e1e", fg="#ffffff", font=("Helvetica", 12))
        self.log_pane.grid(row=3, column=0, columnspan=3, pady=20, sticky="ew")

        self.current_frame.columnconfigure(0, weight=1)
        self.current_frame.columnconfigure(1, weight=0)
        self.current_frame.columnconfigure(2, weight=0)

    def load_model(self):
        model_name = self.model_var.get()
        if model_name:
            self.log(f"Loaded {model_name}")
            self.create_conversation_screen()

            # Start the background script in a separate thread
            self.background_thread = threading.Thread(target=self.run_background_script)
            self.background_thread.start()
        else:
            self.log("No model selected.")

    def unload_model(self):
        self.log("Unloaded model.")
        self.model_var.set("")

    def log(self, message):
        self.log_pane.config(state='normal')
        self.log_pane.insert(tk.END, message + '\n')
        self.log_pane.see(tk.END)
        self.log_pane.config(state='disabled')

    def run_background_script(self):
        # Simulating a background task
        for i in range(1, 6):
            self.log(f"Running background task step {i}")
            # Simulate some work
            import time
            time.sleep(1)
        self.log("Background task completed.")

    def create_conversation_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = ttk.Frame(self.root, padding="20 20 20 20", style='TFrame')
        self.current_frame.grid(row=0, column=0, sticky="nsew")

        self.conversation_pane = scrolledtext.ScrolledText(self.current_frame, wrap=tk.WORD, width=80, height=20, state='disabled', bg="#1e1e1e", fg="#ffffff", font=("Helvetica", 12))
        self.conversation_pane.grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")

        self.user_input_var = tk.StringVar()
        user_input_entry = ttk.Entry(self.current_frame, textvariable=self.user_input_var, width=60, font=("Helvetica", 12))
        user_input_entry.grid(row=1, column=0, pady=10, padx=5, sticky="ew")
        user_input_entry.bind('<Return>', self.send_message)  # Bind the Enter key to send message

        send_button = ttk.Button(self.current_frame, text="Send", command=self.send_message, style='TButton')
        send_button.grid(row=1, column=1, pady=10, sticky="e")

        self.current_frame.columnconfigure(0, weight=1)
        self.current_frame.columnconfigure(1, weight=0)

    def send_message(self, event=None):
        user_message = self.user_input_var.get()
        if user_message:
            self.conversation_pane.config(state='normal')
            self.conversation_pane.insert(tk.END, "You: " + user_message + '\n')
            self.conversation_pane.config(state='disabled')
            self.conversation_pane.yview(tk.END)
            self.user_input_var.set("")
            # Here you can add logic to process the user message and append bot responses to the conversation pane
            print(f"User: {user_message}")

    def check_log_queue(self):
        while True:
            try:
                message = self.log_queue.get_nowait()
                self.console_redirector.write(message)
            except queue.Empty:
                break
        self.root.after(100, self.check_log_queue)

if __name__ == "__main__":
    root = tk.Tk()

    style = ttk.Style()
    style.theme_use('clam')
    
    style.configure('TFrame', background='#2e2e2e')
    style.configure('TLabel', background='#2e2e2e', foreground='#ffffff', font=('Helvetica', 14))
    style.configure('TButton', background='#005f99', foreground='#ffffff', font=('Helvetica', 12, 'bold'))
    style.map('TButton', background=[('active', '#003f66')])

    app = MedalAIApp(root)
    root.protocol("WM_DELETE_WINDOW", root.quit)  # Handle window close event
    root.after(100, app.check_log_queue)  # Start checking log queue
    root.mainloop()
