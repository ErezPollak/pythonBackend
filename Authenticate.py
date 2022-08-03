import hashlib
import random

from Exceptions import AuthenticationError


class Authenticate:

    def __init__(self):
        self.users_dict = {}

    def create_hash(self, user_name: str, password: str) -> int:
        # if user_name in self.users_dict.keys():
        #     raise AuthenticationError("user already in authentication process.")
        r_num = random.randint(0, 100000)
        self.users_dict[user_name] = hashlib.sha256((password + str(r_num)).encode('utf-8')).hexdigest()
        print(self.users_dict[user_name])
        return r_num

    def compare_hash(self, user_name: str, hushed_password: str) -> bool:
        #return True
        if user_name not in self.users_dict.keys():
            raise AuthenticationError("user is not in authentication table!")
        is_verified = self.users_dict[user_name] == hushed_password
        self.users_dict.pop(user_name)
        return is_verified
