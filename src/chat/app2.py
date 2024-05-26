from chat import get_response, bot_name, load_model, unload_model
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import sys
import threading
import queue  # for thread-safe communication
import markdown
from tkhtmlview import HTMLLabel

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
        # Start the queue checking loop
        self.root.after(100, self.check_log_queue)

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
            # Start the background script in a separate thread
            self.background_thread = threading.Thread(target=load_model, args=(model_name,))
            self.background_thread.start()
            self.log("Loading model... Please wait.")
            
            self.background_thread2 = threading.Thread(target=self.wait_and_load_convo_screen, args=(self.background_thread,model_name,))
            self.background_thread2.start()
            
            
        else:
            self.log("No model selected.")

    def unload_model(self):
        self.log("Unloaded model.")
        self.model_var.set("")

    def wait_and_load_convo_screen(self, task, model_name):
        import time
        while task.is_alive():
            time.sleep(0.1)
        
        self.log(f"Loaded {model_name}")
        time.sleep(1)
        self.create_conversation_screen()

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
        
        self.set_window_size(700, 700)
        self.current_frame = ttk.Frame(self.root, padding="20 20 20 20", style='TFrame')
        self.current_frame.grid(row=0, column=0, sticky="nsew")

        self.conversation_pane = HTMLLabel(self.current_frame, wrap=tk.WORD, width=80, height=20, background="#1e1e1e", foreground="#ffffff", font=("Helvetica", 12))
        self.conversation_pane.grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")

        self.user_input_var = tk.StringVar()
        user_input_entry = tk.Text(self.current_frame, width=50, height=3, font=("Helvetica", 12), wrap=tk.WORD, bg="#ffffff", fg="#000000")
        user_input_entry.grid(row=1, column=0, pady=10, padx=5, sticky="ew")
        user_input_entry.bind('<Return>', self.send_message(event=None, user_input=user_input_entry))  # Bind the Enter key to send message
        user_input_entry.bind('<Shift-Return>', lambda event: self.add_newline(event, user_input_entry))

        send_button = ttk.Button(self.current_frame, text="Send", command=lambda: self.send_message(event=None, user_input=user_input_entry), style='TButton')
        send_button.grid(row=1, column=1, pady=10, sticky="e")

        self.current_frame.columnconfigure(0, weight=1)
        self.current_frame.columnconfigure(1, weight=0)
        self.user_input_entry = user_input_entry  # Store reference for later use

    def add_newline(self, event, text_widget):
        text_widget.insert(tk.END, "\n")
        return "break"

    def send_message(self, event=None, user_input=None):
        user_message = user_input.get("1.0", tk.END).strip()
        if user_message:
            self.conversation_pane.set_html(f"<p><strong>You:</strong> {user_message}</p>")
            user_input.delete("1.0", tk.END)
            # self.conversation_pane.config(state='normal')
            # self.conversation_pane.insert(tk.END, "You: " + user_message + '\n')
            # self.conversation_pane.config(state='disabled')
            # self.conversation_pane.yview(tk.END)
            user_input.delete("1.0", tk.END)
            # Here you can add logic to process the user message and append bot responses to the conversation pane
            print(f"User: {user_message}")
        self.full_bot_response_markdown = ""
        self.background_thread = threading.Thread(target=get_response, args=(user_message, self.update_conversation_pane,))
        self.background_thread.start()
        self.update_conversation_pane("MEDAL-AI : ")
        # response = get_response(user_message, self.write_response)
        # self.conversation_pane.insert(tk.CURRENT, f"{bot_name}: ")
        # if response:
        #     self.conversation_pane.config(state='normal')
        #     self.conversation_pane.insert(tk.CURRENT, f"{bot_name}: {response}\n")
        #     self.conversation_pane.config(state='disabled')
        #     self.conversation_pane.yview(tk.END)

    def update_conversation_pane(self, message):
        self.root.after(0, self._update_conversation_pane, message)

    def _update_conversation_pane(self, message):
        self.full_bot_response_markdown += message
        html_content = markdown.markdown(self.full_bot_response_markdown)
        self.conversation_pane.set_html(f"<p> {html_content}</p>")
        self.conversation_pane.yview(tk.END)

        # current_html = self.conversation_pane.html
        # new_html = current_html + f"<p> {message}</p>"
        # self.conversation_pane.set_html(new_html)
        # self.conversation_pane.yview(tk.END)


        # self.conversation_pane.config(state='normal')
        # self.conversation_pane.insert(tk.END, message)
        # self.conversation_pane.config(state='disabled')
        # self.conversation_pane.yview(tk.END)

    def check_log_queue(self):
        while not self.log_queue.empty():
            message = self.log_queue.get_nowait()
            if self.log_pane:
                self.log_pane.config(state='normal')
                self.log_pane.insert(tk.END, message)
                self.log_pane.see(tk.END)
                self.log_pane.config(state='disabled')
            # self.log_pane.config(state='normal')
            # self.log_pane.insert(tk.END, message)
            # self.log_pane.see(tk.END)
            # self.log_pane.config(state='disabled')
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
