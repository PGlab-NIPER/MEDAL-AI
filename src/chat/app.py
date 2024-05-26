from tkinter import *
from tkinter import ttk, filedialog, messagebox
from chat import get_response, bot_name, load_model

import os

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

class ChatApplication:
    
    def __init__(self):
        self.window = Tk()
        self._setup_main_window()
        
        
    def run(self):
        self.window.mainloop()
    
    def clear_window(self):
        # Destroy all widgets in the window
        for widget in self.window.winfo_children():
            widget.destroy()
    
    def _setup_chat_window(self):
        self.window.title("Chat")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=470, height=550, bg=BG_COLOR)
        
        # head label
        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                           text="Welcome", font=FONT_BOLD, pady=10)
        head_label.place(relwidth=1)
        
        # tiny divider
        line = Label(self.window, width=450, bg=BG_GRAY)
        line.place(relwidth=1, rely=0.07, relheight=0.012)
        
        # text widget
        self.text_widget = Text(self.window, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR,
                                font=FONT, padx=5, pady=5)
        self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget.configure(cursor="arrow", state=DISABLED)
        
        # scroll bar
        scrollbar = Scrollbar(self.text_widget)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.configure(command=self.text_widget.yview)
        
        # bottom label
        bottom_label = Label(self.window, bg=BG_GRAY, height=80)
        bottom_label.place(relwidth=1, rely=0.825)
        
        # message entry box
        self.msg_entry = Entry(bottom_label, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)
        
        # send button
        send_button = Button(bottom_label, text="Send", font=FONT_BOLD, width=20, bg=BG_GRAY,
                             command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)

        # self.text_widget = Text(self.window, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR,
        #                         font=FONT, padx=5, pady=5)
        # self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08)
        # self.text_widget.configure(cursor="arrow", state=DISABLED)
        
        # scrollbar = Scrollbar(self.text_widget)
        # scrollbar.place(relheight=1, relx=0.974)
        # scrollbar.configure(command=self.text_widget.yview)
        
        # bottom_label = Label(self.window, text= "NONO", bg=BG_GRAY, height=80)
        # bottom_label.place(relwidth=1, rely=0.825)
        
        # self.msg_entry = Entry(bottom_label, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
        # self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        # self.msg_entry.focus()
        # self.msg_entry.bind("<Return>", self._on_enter_pressed)
        
        # send_button = Button(bottom_label, text="Send", font=FONT_BOLD, width=20, bg=BG_GRAY,
        #                      command=lambda: self._on_enter_pressed(None))
        # send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)


    def _setup_main_window(self):
        self.window.title("Model Loader")

        # Dropdown for model selection
        self.model_var = StringVar()
        model_dropdown = ttk.Combobox(self.window, textvariable=self.model_var)
        model_dropdown['values'] = ("Model A", "Model B", "Model C", "Model D")
        model_dropdown.current(0)  # Set default value
        model_dropdown.pack(pady=10)

        # Button to load model values
        load_button = Button(self.window, text="Load Model", command=self.load_model)
        load_button.pack(side=LEFT, padx=5)

        # Button to load model values
        load_button = Button(self.window, text="Unload Model", command=self.unload_model)
        load_button.pack(side=RIGHT, padx=5)

        # Display box for logs
        self.log_text = StringVar()
        log_display = Label(self.window, textvariable=self.log_text, justify=LEFT, anchor="w", relief="sunken", bg="white", width=50, height=10)
        log_display.pack(pady=20, padx=10, fill=BOTH, expand=True)
     

    def load_model(self):
        selected_model = self.model_var.get()
        self.log_text.set(f"Loading values for {selected_model}...\n")
        # Simulate loading process
        # load_model(selected_model)
        self.log_text.set(self.log_text.get() + f"{selected_model} values loaded successfully.\n")
        self.clear_window()
        self._setup_chat_window()


    def unload_model(self):
        selected_model = self.model_var.get()
        self.log_text.set(f"Unloading values for {selected_model}...\n")
        # Simulate unloading process
        unload_model()
        self.log_text.set(self.log_text.get() + f"{selected_model} values unloaded successfully.\n")

    def list_files(self):
        # Open a directory dialog and get the selected directory
        try:
            # List all files in the given directory
            files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
            
            # Print the files
            for file in files:
                print(file)
        except Exception as e:
            print(f"Error: {e}")

    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        self._insert_message(msg, "You")
        
    def _insert_message(self, msg, sender):
        if not msg:
            return
        
        self.msg_entry.delete(0, END)
        msg1 = f"{sender}: {msg}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg1)
        self.text_widget.configure(state=DISABLED)
        
        msg2 = f"{bot_name}: {get_response(msg)}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg2)
        self.text_widget.configure(state=DISABLED)
        
        self.text_widget.see(END)
             
        
if __name__ == "__main__":
    app = ChatApplication()
    app.run()