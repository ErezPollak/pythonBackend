import socket

from Exceptions import DbAndLogicError


class DL_Client:
    _instance = None

    @staticmethod
    def get_instance():
        if DL_Client._instance is None:
            DL_Client._instance = DL_Client()
        return DL_Client._instance

    def __init__(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(('localhost', 54000))
            print("connection created successfully")
            self.client.send("csizes".encode())

            self.sizes = []
            self.client.recv(4)
            for i in range(3):
                self.sizes += [int.from_bytes(self.client.recv(4), 'little')]
            print("sized are: ", self.sizes)
            print()
        except ConnectionError:
            print("not able to make a connection!")

    def client_communication(self, command: str):
        print("in communication function")
        send_message_size = self.client.send(command.encode())
        print(send_message_size, 'bytes send \nwait for response....')
        size = int.from_bytes(self.client.recv(4), 'little')
        print('size receive:', size)
        response_message = self.client.recv(size).decode()
        print('message received:', response_message)
        if response_message[:5] == 'ERROR':
            raise DbAndLogicError(response_message)
        return response_message
