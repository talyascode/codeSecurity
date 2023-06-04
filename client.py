"""
Author: Talya Gross
CLIENT
"""

# import
from gui import *
import zipfile
import socket
import ssl

BUF = 16000


class Client:
    def __init__(self, port, ip):
        """
            build function of the Client class.
            create ssl layer and a socket
        """
        self.ip = ip
        self.port = port

        # create the ssl context
        self.context = ssl.create_default_context()
        # allow self signed certificate
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE

        print("connecting to the server...")
        self.sock = socket.socket()
        self.conn = self.context.wrap_socket(self.sock, server_hostname=ip)
        print("connected!")
        self.app = None
        self.files = b''
        self.result_dict = {"yes": True, "no": False}

    def start_client(self):
        """
            the function starts a new connection with the server, creates a gui, receives input from the user
            (through the gui), sends the server the information for the simulation and the file data in chunks,
            gets the result of the simulation from the server, saves it to the history database and shows the user
            the results
            here is all the communication with the server after connecting.
        """
        try:
            self.conn.connect((self.ip, self.port))
            while True:
                if not self.app:
                    self.app = SampleApp()
                    self.app.mainloop()
                result = self.app.get_result()
                print(f"data: {result}")
                if result:
                    # send req, param, file length and code path
                    req = result[0]  # sql or ssrf
                    param = result[1]  # parameter for the simulation or None
                    file_path = result[2]  # the whole path to the project in the computer
                    code_path = result[3]  # the specific path to the file in the project
                    name = result[4]
                    msg = req + "\r\n" + param + "\r\n" + str(self.file_length(file_path)) + "\r\n" + code_path
                    self.app = SampleApp()
                    if self.check_exists(code_path, file_path):
                        self.conn.send(str(len(msg)).encode())  # send the length of the msg
                        self.conn.send(msg.encode())
                        server_msg = self.conn.recv(1024).decode()
                        if server_msg == "exit":  # check if the server got all the msg
                            break
                        self.send_file(file_path)  # send file data in chunks
                        result = self.result_dict[self.conn.recv(1024).decode()]
                        if server_msg == "exit":  # check if the server got all the data
                            break
                        self.app.update_history(name, req, code_path, result)
                        self.app.set_name(name)
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
                elif self.app.get_exit:
                    print("exiting...")
                    self.conn.send("exit".encode())
                    break
        except socket.error as err:
            print('received socket exception - ' + str(err))
        except Exception as err:
            print(err)
        finally:
            self.conn.close()
            print("exit.")

    def send_file(self, path):
        """
        the function sends 16000 bytes every time until all data is sent to the server
        param: path: the path to the file
        """
        with open(path, "rb") as zip:
            try:
                # read the contents of the file
                data = zip.read(BUF)
                while data:
                    self.conn.send(data)  # send to server
                    data = zip.read(BUF)
            except UnicodeDecodeError:
                print("Error: Unable to decode file")

    def file_length(self, path):
        """
        :param path: the path to the file
        :return: the length of the file data
        """
        with open(path, "rb") as zip:
            try:
                # read the contents of the file
                data = zip.read()
            except UnicodeDecodeError:
                print("Error: Unable to decode file")
        return len(data)

    def check_exists(self, code_path, file_path):
        """
        :param code_path:  specific code path
        :param file_path: the path to the file
        :return: if the specific code exists in the files
        """
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
