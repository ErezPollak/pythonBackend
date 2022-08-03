class DbAndLogicError(Exception):
    def __init__(self, arg):
        self.args = arg


class BlError(Exception):
    def __init__(self, arg):
        self.args = arg


class UsersError(Exception):
    def __init__(self, arg):
        self.args = arg


class AuthenticationError(Exception):
    def __init__(self, arg):
        self.args = arg
