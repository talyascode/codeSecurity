"""
Author: Talya Gross
SERVER
"""
# import
import os
import socket
import subprocess
import threading
import time
BUF = 16000
FAKE_DATA = '{\n  "image": "user: Admin , password: pass1234!"\n}' # the data we reacive if we mangaed to accces the local server
SQL_INJECTION = "name=talya&pass=' or 1=1;--"
SSRF_URL = "url=http://172.17.0.2:1000/admin"


class Server:
    """
        build function of the Client class.
    """
    def __init__(self, port):
        self.sock = socket.socket()
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen()
        print("server is up")

        """
        ALL CLIENTS:
        ('127.0.0.1', 49944): socket
        ('127.0.0.1', 49942): socket

        """
        self.all_clients = {}
        self.port = 1001

    def wait_for_clients(self):
        """
            the function accepts new clients and calls the handle client in threading
        """
        try:
            while True:
                client_socket, client_address = self.sock.accept()
                self.all_clients[client_address] = client_socket
                print("all clients:")
                print(self.all_clients)
                t = threading.Thread(target=self.handle_client, args=[client_address])
                t.start()
                print("new thread for client:", client_address)
        except socket.error as err:
            print('received socket exception - ' + str(err))
        finally:
            if self.all_clients:
                client_socket = list(self.all_clients.values())[0]
                client_socket.close()
                client_socket = list(self.all_clients.values())[1]
                client_socket.close()

    def handle_client(self, client_address):
        """
            the function receives data from the current client and checks what the data is and acts according
            to the protocol of the program.
        :param client_address: the address of the current client that is being handled
        """
        client_socket = self.all_clients[client_address]
        try:
            while True:
                print("listening to client:", client_address)
                data = client_socket.recv(1024).decode() # rcv req and param and the length
                print(f"data:{data}")
                data = data.split("\r\n")
                req = data[0] # sql or ssrf
                parm = data[1] # none or what the server returns when the condition is true
                length = int(data[2])  # the length of the file
                code_path  = data[3] # code path inside the project
                data = b''
                print("check")
                # receiving the file data from the client
                while True:
                    chunk = client_socket.recv(BUF)
                    length -= len(chunk)
                    data += chunk
                    if length < BUF:
                        chunk = client_socket.recv(length)
                        data += chunk
                        break
                # Write the data to a zip file
                with open('code_files.zip', 'wb') as f:
                    f.write(data)

                print(f"req: {req}, parm: {parm}, files:{data}")
                if req == "ssrf":
                    result = self.check("pfp", code_path, FAKE_DATA, client_address, SSRF_URL)  # retruns True- (yes) or False(no)
                elif req == "sql":
                    result = self.check("input", code_path, parm, client_address, SQL_INJECTION) # retruns True- (yes) or False(no)
                else:
                    #TODO: request is unvalid
                    pass
                    break
                self.port += 1  # changing the port so it wont be the same in the next docker
                print(f"res: {result}")
                client_socket.send(result.encode())
                print("check")
        except socket.error as err:
            print('received socket exception - ' + str(err))
        finally:
            client_socket.close()

    def check(self, url_path, code_path, condition, addr, data):
        """
        send to the docker the code file, the request and the params
        :return:
        """
        try:
            docker_name = str(addr[1])

            # Build the Docker image
            os.system(f'docker build -t {docker_name} .')

            # Run the Docker container in the background
            print(f"port:{self.port}")
            docker_cmd = f'docker run -p {self.port}:{self.port} -e FILE="{code_path}" -e PORT="{self.port}" {docker_name}'
            subprocess.Popen(docker_cmd, shell = True)

            time.sleep(5)  # wait for the docker to run before the curl command

            # simulate a sql injection/ ssrf attack
            print(f"simulation...")
            url = f'http://localhost:{self.port}/{url_path}'
            print(f"url:{url}")
            curl_cmd = ['curl', '-X', 'POST', url, '-d', data]
            process = subprocess.Popen(curl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            answer = stdout.decode()
            print(f"answer:{answer.strip()}, condition:{condition}")
            if condition == answer.strip():
                # the attack succeeded!
                return "yes"
            # the attack didn't succeed!
            return "no"
        except Exception as err:
            print(err)
        finally:
            # removing the docker
            # docker_id = subprocess.check_output(f'docker ps --filter "ancestor={addr[1]}" --format "{{{{.ID}}}}"').strip().decode()
            # os.system(f"docker rm {docker_id} -f")
            pass


def main():
    """
        the main function of the server
    """
    my_server = Server(8000)
    my_server.wait_for_clients()


if __name__ == "__main__":
    # Call the main handler function
    main()
