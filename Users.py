import atexit

from Exceptions import UsersError

USERS_DB_FILE = 'usersDB.bin'
SEPARATION_CHAR = ' '


class Users:

    def __init__(self):
        self.user_dict = {}
        with open(USERS_DB_FILE, 'rb') as f:
            users_lst = f.read().decode().split(SEPARATION_CHAR)
            self.user_dict = dict(zip(users_lst[::2], users_lst[1::2]))

    def find_user(self, name: str) -> bool:
        if name not in self.user_dict.keys():
            raise UsersError("Users Exception: User does not exist in the database.")
        return True

    def creat_user(self, name: str, password: str):
        if name in self.user_dict.keys():
            raise UsersError("Users Exception: User already exist in the database.")
        self.user_dict[name] = password
        self._make_update()

    def set_password(self, name: str, password: str):
        if name not in self.user_dict.keys():
            raise UsersError("Users Exception: User does not exist in the database.")
        self.user_dict[name] = password
        self._make_update()

    def delete_user(self, name: str):
        if name not in self.user_dict.keys():
            raise UsersError("Users Exception: User does not exist in the database.")
        self.user_dict.pop(name)
        self._make_update()

    def get_users_names(self):
        return self.user_dict.keys()

    def _make_update(self):
        atexit._clear()
        atexit.register(self._update_users_file)

    def _update_users_file(self):
        # if self.user_dict == {}:
        #     return
        print("updating users file...")
        print(self.user_dict)
        with open(USERS_DB_FILE, 'wb') as f:
            for key in self.user_dict.keys():
                f.write(f"{key}{SEPARATION_CHAR}{self.user_dict[key]}{SEPARATION_CHAR}".encode())
        print("finish updating users file.")
