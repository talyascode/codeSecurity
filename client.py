"""
Author: Talya Gross
CLIENT
"""
# import
from os.path import exists

from gui import *
import socket
BUF = 16000


class Client:
    """
        build function of the Client class.
    """
    def __init__(self, port, ip):
        print("connecting...")
        self.sock = socket.socket()
        self.sock.connect((ip, port))
        print("connected!")
        self.app = None
        self.files = b''
        self.result_dict = {"yes": True, "no": False}

    def start_client(self):
        """
            the function receives input from the user and according to that it
            starts the game or exits and closes the socket. here is all the communication
             with the server after connecting.
        """
        try:
            # start = input("enter start to start, exit to quit ")
            while True:
                # if start == "start":
                # self.sock.send(start.encode()) # sending start
                # self.sock.send("ssrf user: Admin , password: pass1234!".encode()) # send the parm and req to the server
                self.app = SampleApp()
                self.app.mainloop()
                result = self.app.get_result()
                print(f"data: {result}")
                if result:
                    # 0- req , 1-param, 2- file path, 3- code path
                    # send req and parm and files and code path(in chunks)
                    req = result[0]
                    file_path = result[2]
                    code_path = result[3]
                    msg = req + "\r\n" + result[1] + "\r\n" +str(self.file_length(file_path)) + "\r\n" + code_path
                    self.app = SampleApp()
                    if self.check_exists(code_path, file_path):
                        self.sock.send(msg.encode())  # send the parm and req to the server
                        self.send_file(file_path) # send_file(file_path)
                        result = self.result_dict[self.sock.recv(1024).decode()]
                        print(result)
                        if req == "sql":
                            if result:
                                self.app.show_frame("SqlHacked")
                            else:
                                self.app.show_frame("Sql")
                        elif req == "ssrf":
                            if result:
                                self.app.show_frame("SsrfHacked")
                            else:
                                self.app.show_frame("Ssrf")
                        self.app.mainloop()
                    else:
                        # the file doesnt exists in the zip
                        self.app.show_frame("Error")

            # if start == "exit":
            #     self.sock.send("exit".encode())
            #     print("exiting...")
            #     break
        except socket.error as err:
            print('received socket exception - ' + str(err))
        except Exception as err:
            print(err)
        finally:
            self.sock.close()

    def send_file(self, path):
        length = 0
        with open(path, "rb") as zip:
            try:
                # read the contents of the file
                data = zip.read(BUF)
                while data:
                    self.sock.send(data)  # send to server
                    data = zip.read(BUF)
                    # print(data)
            except UnicodeDecodeError:
                print("Error: Unable to decode file")
        return len(data)

    def file_length(self, path):
        with open(path, "rb") as zip:
            try:
                # read the contents of the file
                data = zip.read()
            except UnicodeDecodeError:
                print("Error: Unable to decode file")
        return len(data)

    def check_exists(self, code_path, file_path):
        import zipfile

        with zipfile.ZipFile(file_path, "r") as my_zip:
            for file_info in my_zip.infolist():
                if file_info.filename == code_path:
                    print(f"{code_path} exists in the zip file.")
                    return True
        print(f"{code_path} does not exist in the zip file.")
        return False


def main():
    """
         the main function of the client
    """
    try:
        my_client = Client(8000, "127.0.0.1")
        my_client.start_client()
    except socket.error as err:
        print('received socket exception - ' + str(err))
        print("couldn't make a connection... try again")
    finally:
        pass  # there is no socket to close when the client wasn't able to connect.


if __name__ == "__main__":
    # Call the main handler function
    main()
