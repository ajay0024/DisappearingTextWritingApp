from tkinter import *
from tkinter import ttk, filedialog
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

class DisappearingText:

    def __init__(self, root):
        self.start_time = time.time();
        root.title("Disappearing Text Writer")
        root.minsize(600, 100)
        root.maxsize(700, 700)
        root.columnconfigure(0, weight=1, minsize=100)
        root.rowconfigure(0, weight=1, minsize=100)

        # Instantiating Style class
        self.style = ttk.Style(root)

        # Changing font-size of all the Label Widget
        # self.style.theme_use('clam')
        self.style.configure("My.TLabel", font=('Trebuchet MS', 25))

        # self.style.configure("TProgressbar", darkcolor="red",background="red", bordercolor="red", lightcolor="blue")

        self.mainframe = ttk.Frame(root, padding="12 12 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=1, minsize=50)
        self.mainframe.rowconfigure(0, weight=0, minsize=20)
        self.mainframe.columnconfigure(1, weight=1, minsize=50)
        self.mainframe.rowconfigure(1, weight=1, minsize=50)
        self.mainframe.rowconfigure(2, weight=1, minsize=50)

        self.target_time = IntVar()
        self.target_time.set(1)
        self.written_text = StringVar()
        self.timer = IntVar()
        self.timer.set(0)
        self.death_timer = IntVar()
        self.timer_percentage_completion = IntVar()
        self.start_death_time = time.time()
        self.wordcount = StringVar(value=0)
        self.text_running = False

        self.create_widgets()
        self.initialize_start_screen()
        self.time_entry.focus()

    def create_widgets(self):
        vcmd = (root.register(self.validate_time_entry), '%P')
        ivcmd = (root.register(self.on_invalid),)
        # Start Screen Widgets
        self.time_entry = ttk.Entry(self.mainframe, textvariable=self.target_time, style="My.TEntry",
                                    font=('Trebuchet MS', 25), width=3)
        self.time_entry.config(validate='key', validatecommand=vcmd, invalidcommand=ivcmd)
        self.label_error = ttk.Label(self.mainframe, foreground='red')
        self.time_entry_label = ttk.Label(self.mainframe, text="Minutes", font=('Trebuchet MS', 25))
        self.submit_button = ttk.Button(self.mainframe, text="Submit", command=self.on_submit)

        # Typing Screen Widgets
        # self.timer_label = ttk.Label(self.mainframe, textvariable=self.timer)
        # self.death_timer_label = ttk.Label(self.mainframe, textvariable=self.death_timer)
        self.text_entry = Text(self.mainframe, width=100, height=20, font=('Trebuchet MS', 12))
        self.timer_line = ttk.Progressbar(self.mainframe, orient=HORIZONTAL, mode="determinate",
                                          variable=self.timer_percentage_completion)
        self.text_entry.bind("<KeyPress>", self.reset_death_timer)

        # Death screen Widgets
        self.death_screen_label = ttk.Label(self.mainframe, text="You cannot stop for more than 5 seconds. Try Again!",
                                            font=('Trebuchet MS', 12), foreground="red")
        self.start_again_button = ttk.Button(self.mainframe, text="Try Again!", command=self.initialize_start_screen)

    def initialize_start_screen(self):
        self.clear_mainframe()
        self.label_error.grid(row=0, column=0, sticky=N, columnspan=2)
        self.time_entry.grid(row=1, column=0, sticky=SE)
        self.time_entry_label.grid(row=1, column=1, sticky=SW, padx=10)
        self.submit_button.grid(row=2, column=0, columnspan=2, sticky=N, pady=20)

    def show_message(self, error='', color='black'):
        self.label_error['text'] = error
        self.time_entry.focus()

    def validate_time_entry(self, value):
        # print(len(value))
        if len(value) > 0:
            if not value.isnumeric() or int(value) > 120:
                return False
        self.show_message()
        return True

    def clear_mainframe(self):
        for x in self.mainframe.winfo_children():
            x.grid_forget()

    def on_invalid(self):
        self.show_message('Please enter a valid number upto 120', 'red')

    def on_submit(self):
        try:
            if self.target_time.get() < 1:
                self.show_message('Please enter a valid number upto 120', 'red')
            else:
                self.start_typing_screen()
        except TclError:
            self.show_message('Please enter a valid number upto 120', 'red')

    def start_typing_screen(self):
        self.text_running = True
        self.clear_mainframe()
        self.start_time = time.time()
        self.start_death_time = time.time()
        self.start_timer()
        self.start_death_timer()
        self.start_coloring()

        self.timer_line.grid(column=0, row=0, columnspan=2, sticky=(E, W))
        # self.timer_label.grid(column=0, row=1)
        # self.death_timer_label.grid(column=1, row=1)
        self.text_entry.grid(column=0, row=2, sticky=(N, E, W, S), columnspan=2)
        scrollbar = Scrollbar(self.mainframe, orient=VERTICAL, command=self.text_entry.yview)
        scrollbar.grid(column=2, row=2, sticky=(N, S))
        self.text_entry.configure(yscrollcommand=scrollbar.set)

        print("starting typing")

    def time_over(self):
        self.text_running = False
        text = self.text_entry.get("1.0", "end")
        filename = filedialog.asksaveasfilename(defaultextension=".doc",
                                                filetypes=(("PDF file", "*.pdf"), ("All Files", "*.*")))
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4,
                                    rightMargin=2 * cm, leftMargin=2 * cm,
                                    topMargin=2 * cm, bottomMargin=2 * cm)

            doc.build([Paragraph(text.replace("\n", "<br />"), getSampleStyleSheet()['Normal']), ])
        except FileNotFoundError:
            print("Didn't want to save.")

        self.initialize_start_screen()
        self.text_entry.delete("1.0", "end")
        print("Time Over")

    def death_time_over(self):
        self.text_running = False
        self.text_entry.delete("1.0", "end")
        self.clear_mainframe()
        self.death_screen_label.grid(row=1, column=0, columnspan=2, sticky=S)
        self.start_again_button.grid(row=2, column=0, columnspan=2, sticky=N)

    def start_timer(self):
        self.timer.set(int(time.time() - self.start_time))
        self.timer_percentage_completion.set(self.timer.get() / (self.target_time.get() * 60) * 100)
        print(self.timer_percentage_completion.get())
        if self.timer_percentage_completion.get() > 100:
            self.time_over()
        if self.text_running:
            root.after(1000, self.start_timer)

    def start_coloring(self):
        if float(self.death_timer.get()) >= 2:
            diff = float(time.time() - self.start_death_time) - 2
            if 0 < diff <= 3:
                current_color_gb = hex(int(255 - (255 / 3) * diff)).lstrip("0x")
                current_color_gb = "00" if current_color_gb == "" else current_color_gb
                current_color_gb = "0" + current_color_gb if len(current_color_gb) == 1 else current_color_gb
                current_color = "#ff" + current_color_gb + current_color_gb
                self.text_entry.configure(background=current_color)
        else:
            current_color = "#ffffff"
            self.text_entry.configure(background=current_color)

        if self.text_running:
            root.after(100, self.start_coloring)

    def start_death_timer(self):
        self.death_timer.set(int(time.time() - self.start_death_time))
        if int(self.death_timer.get()) >= 5:
            self.death_time_over()
        if self.text_running:
            root.after(1000, self.start_death_timer)

    def reset_death_timer(self, e):
        # print(e)
        self.start_death_time = time.time()


root = Tk()
# windll.shcore.SetProcessDpiAwareness(1)
DisappearingText(root)
root.mainloop()
