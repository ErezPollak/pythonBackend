from DataCommunication import DL_Client
from Exceptions import DbAndLogicError, BlError


def _command_attribute(payload: str, ch: str) -> str:
    return f"{ch}{payload}" if payload != "" else ''


def _dict_cubes(cube: str) -> dict:
    lst = list(filter(lambda ch: ch != '', cube.split(chr(0))))
    return dict(zip(lst[::3], lst[2::3]))


class BlCubes:
    def __init__(self, owner: str):
        self.dl = DL_Client.get_instance()
        self.owner_name = owner
        self.cube_name = ''

    def read_all_cubes(self) -> str:
        return list(self._generate_command(operation='all').keys())

    def select_cube(self, cube_name: str = ''):
        self.cube_name = cube_name

    def create_cube(self) -> str:
        return list(self._generate_command(operation='create').values())[0]

    def read_cube(self) -> str:
        if self.cube_name == "":
            raise BlError("no cube was selected to read from!")
        return list(self._generate_command(operation='read').values())[0]

    def write_cube(self, payload: str) -> str:
        if self.cube_name == "":
            raise BlError("no cube was selected to write to!")
        return list(self._generate_command(operation='write', payload=payload).values())[0]

    def delete_cube(self) -> str:
        if self.cube_name == "":
            raise BlError("no cube was selected to delete!")
        return list(self._generate_command(operation='delete').values())[0]

    def _generate_command(self, payload="", operation="") -> dict:
        command = f"{_command_attribute(self.cube_name, 'n')},{_command_attribute(self.owner_name, 'o')}," \
                  f"{_command_attribute(payload, 's')},{_command_attribute(operation, 'c')}"
        try:
            response = self.dl.client_communication(command)
        except DbAndLogicError as e:
            raise BlError('BL inner Exception: ' + ''.join(e.args))
        return _dict_cubes(response)

    def solve_cube(self, goal_state="", algorithm="") -> str:
        pass
