import tkinter as tk
import zipfile
from tkinter import font as tkfont, filedialog
from tkinter.filedialog import askopenfile

SCREEN = "800x400"


class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title_font = tkfont.Font(family='Helvetica', size=12, weight="bold", slant="italic")
        self.geometry(SCREEN)
        self.input = None
        self.req = None
        self.file_path = None
        self.code_path = None

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, Ssrf, SsrfHacked, Sql, SqlHacked, Error):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def on_exit(self):
        self.destroy()

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def set_input(self, input):
        """
        retrieves the input from the user and stores it in the input_value attribute.
        """
        self.input= input

    def set_req(self, req):
        """
        retrieves the input from the user and stores it in the input_value attribute.
        """
        self.req = req

    def set_code_path(self, code_path):
        """
        retrieves the input from the user and stores it in the input_value attribute.
        """
        self.code_path = code_path

    def get_result(self):
        """
        returns the value stored in the input_value attribute.
        """
        if self.req and self.input and self.file_path and self.code_path:
            return [self.req, self.input, self.file_path, self.code_path]

    def upload_file(self):
        self.file_path = filedialog.askopenfilename()
        print("Selected file:", self.file_path)


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Welcome! chose a vulnerability to test on your code!", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Sql Injection",
                            command=lambda: controller.show_frame("PageOne"))
        button2 = tk.Button(self, text="Ssrf",
                            command=lambda: controller.show_frame("PageTwo"))
        button1.pack()
        button2.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="Sql Injection Test\n Enter what the server returns when the condition is true:",
                         font=controller.title_font)
        title.pack(side="top", fill="x", pady=10)

        self.condition = tk.Entry(self) # input
        self.condition.pack()

        title = tk.Label(self, text="Enter the path to the server file:",
                         font=controller.title_font)
        title.pack(side="top", fill="x", pady=7)

        self.path = tk.Entry(self)  # input
        self.path.pack()

        upload_button = tk.Button(self, text="Upload", command=controller.upload_file) # upload code files
        upload_button.pack()

        submit_button = tk.Button(self, text="Submit", command=self.submit) # submit button
        submit_button.pack()

        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage")) # home button
        button.pack()

    def submit(self):
        condition = self.condition.get() # Get the user input from the Entry widget
        path = self.path.get()
        print("User input:", condition, path)
        self.controller.set_input(condition)
        self.controller.set_req("sql")
        self.controller.set_code_path(path)
        self.controller.destroy()


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="Ssrf Test\n Enter the path to the server file:",
                         font=controller.title_font)
        title.pack(side="top", fill="x", pady=10)

        self.path = tk.Entry(self)  # input
        self.path.pack()

        upload_button = tk.Button(self, text="Upload", command=controller.upload_file)  # upload code files
        upload_button.pack()

        submit_button = tk.Button(self, text="Submit", command=self.submit)  # submit button
        submit_button.pack()

        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))  # home button
        button.pack()

    def submit(self):
        path = self.path.get()
        print("User input:", path)
        self.controller.set_input("none")
        self.controller.set_req("ssrf")
        self.controller.set_code_path(path)
        self.controller.destroy()


class SqlHacked(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="It seems like your code is vulnerable for sql injection:( \n, here are some tips to fix it:\n - use parameterized queries, like this:"
                                    '\n cursor.execute("SELECT * FROM login WHERE name = ''{0}'' AND password = ''{1}'''".format(name, password))"
                         '\n The parameters are passed as an input to the query method. \n Internally, the query method ensures that the input parameters are \n interpreted literally and not as separate SQL statements.' , font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)


class Sql(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Great! your code isn't vulnerable for sql injection :)", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)


class Ssrf(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Great! your code isn't vulnerable for ssrf :)", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)


class SsrfHacked(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="It seems like your code is vulnerable for ssrf:( \n, here are some tips to fix it:\n -create an allow list of the only domains you allow the client", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)


class Error(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="There is an error in your input, try again", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()