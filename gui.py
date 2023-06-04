"""
Author: Talya Gross
GUI
"""

# import
import hashlib
import tkinter as tk
from tkinter import font as tkfont, filedialog
import sqlite3
import datetime

SCREEN = "700x500"  # the size of the screen
SQL = "SELECT * FROM login WHERE name = '%s' AND password = '%s'"
DATABASE = "data.db"
vulnerability = {"ssrf": "ssrf", "sql": "sql injection"}
result_dict = {True: "was", False: "wasn't"}
EMPTY_MD5 = "d41d8cd98f00b204e9800998ecf8427e"  # an empty string in md5


class SampleApp(tk.Tk):
    """
    The main application class that serves as the GUI container.
    """
    def __init__(self):
        """
        build function of the SampleApp class.
        the container is where we'll stack a bunch of frames
        on top of each other, then the one we want visible
        will be raised above the others
        """
        tk.Tk.__init__(self)

        self.title_font = tkfont.Font(family='Helvetica', size=20, weight="bold", slant="italic")
        self.text_font = tkfont.Font(family='Helvetica', size=15, slant="italic")
        self.buttons_font = tkfont.Font(family='Helvetica', size=10, weight="bold", slant="italic")
        self.geometry(SCREEN)
        self.input = None  # the data for the simulation or None
        self.req = None
        self.file_path = ""
        self.code_path = None
        self.exit = False
        self.name = ""

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, Ssrf, SsrfHacked,
                  Sql, SqlHacked, Error, Registration, SignupPage, LoginPage, History, LoginOrSignErr):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("Registration")

    def on_exit(self):
        """
        Handles the event when the user exits the application.
        It sets the "exit" flag to True and destroys the GUI window.
        """
        self.exit = True
        self.destroy()

    def get_name(self):
        """
        return: the name of the user currently logged in.
        """
        return self.name

    def set_name(self, name):
        """
        setting the name and updating the frames with the name of the user
        :param name: the name of the user
        """
        self.name = name
        self.frames["StartPage"].update_name_label()
        self.frames["History"].update_name_label()

    def history(self):
        """
        calls the function to select history from the database and shows the history frame
        """
        self.frames["History"].select_history()
        self.show_frame("History")

    def show_frame(self, page_name):
        """
        Show a frame for the given page name
        """
        frame = self.frames[page_name]
        frame.tkraise()

    def set_input(self, user_input):
        """
        sets the input- the data from the user
        """
        self.input = user_input

    def set_req(self, req):
        """
         Sets the type of vulnerability (SQL injection or SSRF) for the code execution.
        """
        self.req = req

    def set_code_path(self, code_path):
        """
        sets the code path
        """
        self.code_path = code_path

    def get_result(self):
        """
        returns all the input from the user if everything is filled-
        request, input, file_path, code_path, name
        """
        if self.req and self.input and self.file_path and self.code_path:
            return [self.req, self.input, self.file_path, self.code_path, self.name]

    def get_exit(self):
        """
        return: the current situation of the exit
        """
        return self.exit

    def upload_file(self):
        """
        Opens a file dialog to allow the user to select a file and sets the file path.
        """
        self.file_path = filedialog.askopenfilename()
        print("Selected file:", self.file_path)

    def check_info(self, name, password):
        """
        Connects to the database, verifies the provided user data (name and password),
        and returns True if the name matches the password; otherwise, returns False.
        """
        if password == EMPTY_MD5:
            return False
        conn = None
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE name = ? AND password = ?", (name, password))
            result = cursor.fetchone()
            print(f"result: {result}")
            if result:
                return True
            else:
                return False
        except sqlite3.Error or sqlite3.Warning as err:
            print(f"sql error:{err}")
        finally:
            if conn:
                conn.close()

    def update_history(self, name, req, file_path, result):
        """
        update the user's history in the database
        """
        conn = None
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            history = f"In the {file_path.split('/')[-1].split('.')[0]} code file there {result_dict[result]} a {vulnerability[req]} vulnerability"
            cursor.execute("INSERT INTO history (name, history, date) VALUES (?, ?, ?)", (name, history, datetime.date.today().strftime('%Y-%m-%d')))
        except sqlite3.Error or sqlite3.Warning as err:
            print(f"sql error:{err}")
        finally:
            if conn:
                conn.commit()
                conn.close()

    def new_user(self, name, password):
        """
        create a new user in the database with the given name and password
        """
        conn = None
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, password))
        except sqlite3.Error or sqlite3.Warning as err:
            print(f"sql error:{err}")
        finally:
            if conn:
                conn.commit()
                conn.close()

    def log_out(self):
        """
         Logs out the current user, resetting the name to None, and shows the Registration frame.
        """
        self.name = None
        self.show_frame("Registration")


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        """
        The constructor function for the StartPage frame.
        It sets up the labels, buttons, and their associated commands.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # hello name
        self.name_label = tk.Label(self, text=f"Hello{controller.name}", font=controller.text_font)
        self.name_label.pack(side="top", padx=10, anchor="nw")

        # log out
        log_out = tk.Button(self, text="log out", font=controller.buttons_font, width=6, height=1, bg="#D3E1F3",
                            command=lambda: controller.log_out())
        log_out.pack(side="left", padx=10, anchor="nw")

        # welcome
        label = tk.Label(self, text="Welcome!\n choose a vulnerability to test on your code!", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Sql Injection", font=controller.buttons_font, width=20, height=2,  bg="#D3E1F3",
                            command=lambda: controller.show_frame("PageOne"))
        button2 = tk.Button(self, text="SSRF", font=controller.buttons_font, width=20, height=2, bg="#D3E1F3",
                            command=lambda: controller.show_frame("PageTwo"))
        button1.pack(pady=30)
        button2.pack()

        history = tk.Button(self, text="code history", font=controller.buttons_font, width=20, height=2, bg="#D3E1F3",
                            command=lambda: controller.history())
        history.pack(pady=90)

    def update_name_label(self):
        """
        Updates the name label with the provided name.
        param: name: the name of the user
        """
        self.name_label.config(text=f"Hello {self.controller.name}")


class History(tk.Frame):

    def __init__(self, parent, controller):
        """
        The constructor function for the History frame. It sets up the labels, history display area, and home button.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # hello name
        self.name_label = tk.Label(self, text=f"Hello {self.controller.name}", font=self.controller.text_font)
        self.name_label.pack(side="top", padx=10, anchor="nw")

        label = tk.Label(self, text=f"Code history:", font=self.controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        self.history = tk.Label(self, text="", font=self.controller.text_font)
        self.history.pack(side="top", fill="x", pady=10)

        self.image = tk.PhotoImage(file='home.png')  # store the PhotoImage object in an instance variable
        button = tk.Button(self, image=self.image,
                           command=lambda: self.controller.show_frame("StartPage"))  # home button
        button.pack(pady=50)

    def update_name_label(self):
        """
        Updates the name label with the provided name.
        param: name: the name of the user
        """
        self.name_label.config(text=f"Hello {self.controller.name}")

    def select_history(self):
        """
         Fetches and displays the user's code execution history from the database.
        """
        # select history from database
        conn = None
        results = None
        new_results = ""
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM history WHERE name = ?", (self.controller.name,))
            results = cursor.fetchall()
            for row in results:
                print(f"resultt: {row}")
        except sqlite3.Error or sqlite3.Warning as err:
            print(f"sql error:{err}")
        finally:
            if conn:
                conn.close()
        for result in results:
            new_results += f"date: {result[2]} \n {result[1]}\n"

        self.history.config(text=new_results)


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        """
        The constructor function for the PageOne frame.
        It sets up the labels, input fields, upload button, submit button, and home button.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="Sql Injection Test\n",
                         font=controller.title_font)
        title.pack(side="top", fill="x", pady=10)

        title = tk.Label(self, text="Enter what the server returns when the condition is true:",
                         font=controller.text_font)
        title.pack(side="top", fill="x")

        self.condition = tk.Entry(self)  # input
        self.condition.pack()

        title = tk.Label(self, text="Enter the path to the server file:",
                         font=controller.text_font)
        title.pack(side="top", fill="x", pady=14)

        self.path = tk.Entry(self)  # input
        self.path.pack()

        upload_button = tk.Button(self, text="Upload", font=controller.buttons_font, width=14, height=1,  bg="#D3E1F3",
                                  command=controller.upload_file)  # upload code files
        upload_button.pack(pady=10)

        submit_button = tk.Button(self, text="Submit", font=controller.buttons_font, width=20, height=2,  bg="#D3E1F3",
                                  command=self.submit)  # submit button
        submit_button.pack(pady=20)

        self.image = tk.PhotoImage(file='home.png')  # store the PhotoImage object in an instance variable
        button = tk.Button(self, image=self.image,
                           command=lambda: controller.show_frame("StartPage"))  # home button
        button.pack(pady=50)

    def submit(self):
        """
        Retrieves the user input from the Entry widgets, sets the input data, vulnerability type,
        and code path in the controller, and destroys the frame.
        """
        condition = self.condition.get()  # Get the user input from the Entry widget
        path = self.path.get()
        print("User input:", condition, path)
        self.controller.set_input(condition)
        self.controller.set_req("sql")
        self.controller.set_code_path(path)
        self.controller.destroy()


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        """
        The constructor function for the PageTwo frame.
        It sets up the labels, input field, upload button, submit button, and home button.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="Ssrf Test:",
                         font=controller.title_font)
        title.pack(side="top", fill="x", pady=10)

        title = tk.Label(self, text="Enter the path to the server file:",
                         font=controller.text_font)
        title.pack(side="top", fill="x", pady=14)

        self.path = tk.Entry(self)  # input
        self.path.pack()

        upload_button = tk.Button(self, text="Upload", font=controller.buttons_font, width=14, height=1, bg="#D3E1F3",
                                  command=controller.upload_file)  # upload code files
        upload_button.pack(pady=10)

        submit_button = tk.Button(self, text="Submit", font=controller.buttons_font, width=20, height=2, bg="#D3E1F3",
                                  command=self.submit)  # submit button
        submit_button.pack(pady=20)

        self.image = tk.PhotoImage(file='home.png')  # store the PhotoImage object in an instance variable
        button = tk.Button(self, image=self.image,
                           command=lambda: controller.show_frame("StartPage"))  # home button
        button.pack(pady=50)

    def submit(self):
        """
        Retrieves the user input from the Entry widget, sets the input data, vulnerability type,
        and code path in the controller, and destroys the frame.
        """
        path = self.path.get()
        print("User input:", path)
        self.controller.set_input("none")
        self.controller.set_req("ssrf")
        self.controller.set_code_path(path)
        self.controller.destroy()


class SqlHacked(tk.Frame):

    def __init__(self, parent, controller):
        """
        The constructor function for the SqlHacked frame.
        It sets up the label displaying tips to fix the SQL injection vulnerability and a home button.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="It seems like your code is vulnerable for sql injection:( \n, here are some tips to fix it:\n - use parameterized queries, like this:"
                                    '\n cursor.execute("SELECT * FROM login WHERE name = ''{0}'' \n AND password = ''{1}'''".format(name, password))"
                         '\n The parameters are passed as an input to the query method. \n Internally, the query method ensures that the input parameters are \n interpreted literally and not as separate SQL statements.',
                         font=controller.text_font)
        label.pack(side="top", fill="x", pady=10)

        self.image = tk.PhotoImage(file='home.png')  # store the PhotoImage object in an instance variable
        button = tk.Button(self, image=self.image,
                           command=lambda: controller.show_frame("StartPage"))  # home button
        button.pack(pady=50)


class Sql(tk.Frame):

    def __init__(self, parent, controller):
        """
        The constructor function for the Sql frame.
        It sets up the label displaying there is no SQL injection vulnerability and a home button.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Great! your code isn't vulnerable for sql injection :)", font=controller.text_font)
        label.pack(side="top", fill="x", pady=10)

        self.image = tk.PhotoImage(file='home.png')  # store the PhotoImage object in an instance variable
        button = tk.Button(self, image=self.image,
                           command=lambda: controller.show_frame("StartPage"))  # home button
        button.pack(pady=50)


class Ssrf(tk.Frame):

    def __init__(self, parent, controller):
        """
        The constructor function for the Ssrf frame.
        It sets up the label displaying there is no SSRF vulnerability and a home button.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Great! your code isn't vulnerable for ssrf :)", font=controller.text_font)
        label.pack(side="top", fill="x", pady=10)

        self.image = tk.PhotoImage(file='home.png')  # store the PhotoImage object in an instance variable
        button = tk.Button(self, image=self.image,
                           command=lambda: controller.show_frame("StartPage"))  # home button
        button.pack(pady=50)


class SsrfHacked(tk.Frame):

    def __init__(self, parent, controller):
        """
        The constructor function for the SsrfHacked frame.
        It sets up the label displaying tips to fix the SSRF vulnerability and a home button
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="It seems like your code is vulnerable for ssrf:( \n, here are some tips to fix it:\n -create an allow list of the only domains you allow the client", font=controller.text_font)
        label.pack(side="top", fill="x", pady=10)

        self.image = tk.PhotoImage(file='home.png')  # store the PhotoImage object in an instance variable
        button = tk.Button(self, image=self.image,
                           command=lambda: controller.show_frame("StartPage"))  # home button
        button.pack(pady=50)


class Error(tk.Frame):
    def __init__(self, parent, controller):
        """
        The constructor function for the Error frame.
        It sets up the input error label and a home button
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="There is an error in your input, try again", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        self.image = tk.PhotoImage(file='home.png')  # store the PhotoImage object in an instance variable
        button = tk.Button(self, image=self.image,
                           command=lambda: controller.show_frame("StartPage"))  # home button
        button.pack(pady=50)


class LoginPage(tk.Frame):

    def __init__(self, parent, controller):
        """
        The constructor function for the Login frame.
        It sets up the labels, entry fields for name and password, login button, submit button, and error label.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # login
        label = tk.Label(self, text="Login", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        # name
        label = tk.Label(self, text="name:", font=controller.text_font)
        label.pack(side="top", fill="x", pady=10)
        self.name = tk.Entry(self)  # input
        self.name.pack()

        # password
        label = tk.Label(self, text="password:", font=controller.text_font)
        label.pack(side="top", fill="x", pady=10)
        self.password = tk.Entry(self)  # input
        self.password.pack()

        upload_button = tk.Button(self, text="Submit", font=controller.buttons_font, width=25, height=2, bg="#D3E1F3",
                                  command=self.submit)  # check user's info
        upload_button.pack(pady=10)

    def submit(self):
        """
        Retrieves the user input from the Entry widgets, calls the check_info function in the controller
        to verify the login details, and performs actions based on the result (success or failure).
        """
        name = self.name.get()  # Get the user input from the Entry widget
        self.controller.set_name(name)
        password = hashlib.md5(self.password.get().encode()).hexdigest()
        print("User input:", name, password)
        result = self.controller.check_info(name, password)
        print(result)
        if result:  # logged in successfully!
            self.controller.show_frame("StartPage")
        else:
            self.controller.show_frame("LoginOrSignErr")


class SignupPage(tk.Frame):

    def __init__(self, parent, controller):
        """
        The constructor function for the SignupPage frame.
        It sets up the labels, entry fields for name and password, and submit button.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Sign Up", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        # name
        label = tk.Label(self, text="name:", font=controller.text_font)
        label.pack(side="top", fill="x", pady=10)
        self.name = tk.Entry(self)  # input
        self.name.pack()

        # password
        label = tk.Label(self, text="password:", font=controller.text_font)
        label.pack(side="top", fill="x", pady=10)
        self.password = tk.Entry(self)  # input
        self.password.pack()

        upload_button = tk.Button(self, text="Submit", font=controller.buttons_font, width=25, height=2, bg="#D3E1F3",
                                  command=self.submit)
        upload_button.pack(pady=10)

    def submit(self):
        """
        Retrieves the user input from the Entry widgets, calls the new_user function in the controller to
        create a new user in the database, and performs actions based on the result (success or failure).
        """
        name = self.name.get()
        self.controller.set_name(name)
        password = hashlib.md5(self.password.get().encode()).hexdigest()
        print("sign up - User input:", name, password)
        if name and password != EMPTY_MD5:  # sign in successfully!
            self.controller.new_user(name, password)
            self.controller.show_frame("StartPage")
        else:
            self.controller.show_frame("LoginOrSignErr")


class Registration(tk.Frame):

    def __init__(self, parent, controller):
        """
        The constructor function for the Registration frame.
        It sets up the buttons for signing up or loging in.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Code Security- Registration", font=controller.title_font)
        label.place(relx=0.5, rely=0.2, anchor="center")

        # sign up button
        signup_button = tk.Button(self, text="Sign Up", font=controller.buttons_font, width=25, height=2, bg="#D3E1F3",
                                  command=lambda: self.controller.show_frame("SignupPage"))
        signup_button.place(relx=0.5, rely=0.4, anchor="center")

        # login button
        login_button = tk.Button(self, text="Log In", font=controller.buttons_font, width=25, height=2, bg="#D3E1F3",
                                 command=lambda: self.controller.show_frame("LoginPage"))
        login_button.place(relx=0.5, rely=0.55, anchor="center")


class LoginOrSignErr(tk.Frame):

    def __init__(self, parent, controller):
        """
        The constructor function for the LoginOrSignErr frame.
        It sets up the input error label and home page to go back to Registration.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="There is an error in your input, try again", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        self.image = tk.PhotoImage(file='home.png')  # store the PhotoImage object in an instance variable
        button = tk.Button(self, image=self.image,
                           command=lambda: controller.show_frame("Registration"))  # home button
        button.pack(pady=50)


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
