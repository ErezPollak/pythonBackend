from typing import Union

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from enum import Enum

from Authenticate import Authenticate
from BlCubes import BlCubes
from Exceptions import BlError, UsersError, AuthenticationError
from Users import Users

app = FastAPI()
users = Users()
authentication = Authenticate()
users_cubers_interfaces: dict = {}


class Statuses(Enum):
    SUCCESS = 0
    USER_ERROR = 1
    BL_ERROR = 2
    AuthenticationError = 3


JSON_STATUS_KEY = "Status"
JSON_DESC_KEY = "Description"
JSON_CUBE_KEY = "Response"
JSON_CUBE_LIST_KEY = "Response"


@app.post('/users/create')
async def creat_user(user_name: str, new_password: str, request: Request):
    global users, users_cubers_interfaces
    try:
        users.creat_user(user_name, new_password)
        response = {
            JSON_STATUS_KEY: Statuses.SUCCESS,
            JSON_DESC_KEY: "user was created successfully!"
        }
    except UsersError as e:
        response = {
            JSON_STATUS_KEY: Statuses.USER_ERROR,
            JSON_DESC_KEY: ''.join(e.args)
        }
    return response


@app.get("/users/authenticate")
async def authenticate(user_name: str, request: Request):
    try:
        users.find_user(user_name)
        r_int = authentication.create_hash(user_name, users.user_dict[user_name])
        response = {JSON_STATUS_KEY: Statuses.SUCCESS,
                    JSON_DESC_KEY: str(r_int)}
    except UsersError as e:
        response = {JSON_STATUS_KEY: Statuses.USER_ERROR,
                    JSON_DESC_KEY: ''.join(e.args)}
    except AuthenticationError as e:
        response = {JSON_STATUS_KEY: Statuses.AuthenticationError,
                    JSON_DESC_KEY: ''.join(e.args)}
    finally:
        return response


def authenticate_warp(func):
    def wrapper(user_name: str, hashed_password: str, *args, **kwargs):
        try:
            users.find_user(user_name)
            if authentication.compare_hash(user_name, hashed_password):
                response_json = func(*args, **kwargs)
            else:
                response_json = {JSON_STATUS_KEY: Statuses.USER_ERROR,
                                 JSON_DESC_KEY: "password incorrect!!!"}
        except UsersError as e:
            response_json = {JSON_STATUS_KEY: Statuses.USER_ERROR,
                             JSON_DESC_KEY: ''.join(e.args)}
        except AuthenticationError as e:
            response_json = {JSON_STATUS_KEY: Statuses.AuthenticationError,
                             JSON_DESC_KEY: ''.join(e.args)}
        except BlError as e:
            response_json = {JSON_STATUS_KEY: Statuses.BL_ERROR,
                             JSON_DESC_KEY: ''.join(e.args)}
        finally:
            return response_json

    return wrapper


@app.get("/users/handshake")
async def hand_shake(user_name: str, hashed_password: str, request: Request):
    @authenticate_warp
    def _hand_shake_imp(user_name: str):
        global users_cubers_interfaces
        users_cubers_interfaces[user_name] = BlCubes(user_name)
        return {JSON_STATUS_KEY: Statuses.SUCCESS,
                JSON_DESC_KEY: "user hand-shook successfully!",
                JSON_CUBE_LIST_KEY: str(users_cubers_interfaces[user_name].read_all_cubes())}

    return _hand_shake_imp(user_name, hashed_password, user_name)


@app.get('/users/all')
async def get_all_users(request: Request):
    return {
        JSON_STATUS_KEY: Statuses.SUCCESS,
        "users": {
            user: {
                'password': users.user_dict[user],
                'cubes': str(users_cubers_interfaces[
                                 user].read_all_cubes()) if user in users_cubers_interfaces.keys() else "no hand shake yet",
                'selected': users_cubers_interfaces[
                    user].cube_name if user in users_cubers_interfaces.keys() else "no hand shake yet"
            } for user in users.user_dict
        }
    }


@app.put('/users/set_password')
async def set_user_password(user_name: str, hashed_password: str, new_password: str, request: Request):
    @authenticate_warp
    def _set_user_password_imp(user_name: str, new_password: str):
        global users
        users.set_password(user_name, new_password)
        return {JSON_STATUS_KEY: Statuses.SUCCESS,
                JSON_DESC_KEY: "password changed successfully."}

    return _set_user_password_imp(user_name, hashed_password, user_name, new_password)


@app.delete('/users/delete')
async def delete_user(user_name: str, hashed_password: str, request: Request):
    @authenticate_warp
    def delete_user_imp(user_name: str):
        global users
        users.delete_user(user_name)
        return {JSON_STATUS_KEY: Statuses.SUCCESS,
                JSON_DESC_KEY: "user deleted successfully. "}

    return delete_user_imp(user_name, hashed_password, user_name)


def cubes_warp(func):
    def wrapper(user_name: str, *args, **kwargs):
        if user_name in users_cubers_interfaces.keys():
            response = func(*args, **kwargs)
        else:
            response = {JSON_STATUS_KEY: Statuses.BL_ERROR,
                        JSON_DESC_KEY: "user has not hand-shook yet."}
        return response

    return wrapper


@app.put('/cubes/select')
async def select_cube(user_name: str, hashed_password: str, cube_name: str, request: Request):
    @authenticate_warp
    @cubes_warp
    def select_cube_imp(user_name: str, cube_name: str):
        if cube_name in users_cubers_interfaces[user_name].read_all_cubes():
            users_cubers_interfaces[user_name].select_cube(cube_name)
            return {JSON_STATUS_KEY: Statuses.SUCCESS,
                    JSON_CUBE_KEY: users_cubers_interfaces[user_name].read_cube(),
                    JSON_DESC_KEY: f"cube {cube_name} was chosen successfully. "}
        else:
            return {
                JSON_STATUS_KEY: Statuses.BL_ERROR,
                JSON_DESC_KEY: "the cube is not form the list of existing cubes!!"
            }

    return select_cube_imp(user_name, hashed_password, user_name, user_name, cube_name)


@app.put('/cubes/all')
async def read_all_cubes(user_name: str, hashed_password: str, request: Request):
    @authenticate_warp
    @cubes_warp
    def _read_all_cubes_imp(user_name: str):
        return {JSON_STATUS_KEY: Statuses.SUCCESS,
                JSON_CUBE_LIST_KEY: str(users_cubers_interfaces[user_name].read_all_cubes())}

    return _read_all_cubes_imp(user_name, hashed_password, user_name)


@app.post('/cubes/create')
async def create_cube(user_name: str, hashed_password: str, cube_name: str, request: Request):
    @authenticate_warp
    @cubes_warp
    def _create_cube_imp(user_name: str, cube_name: str):
        users_cubers_interfaces[user_name].select_cube(cube_name)
        users_cubers_interfaces[user_name].create_cube()
        return {
            JSON_STATUS_KEY: Statuses.SUCCESS,
            JSON_DESC_KEY: "cube created successfully.",
            JSON_CUBE_KEY: users_cubers_interfaces[user_name].read_cube()
        }

    return _create_cube_imp(user_name, hashed_password, user_name, user_name, cube_name)


@app.get('/cubes/read')
async def read_cube(user_name: str, hashed_password: str, request: Request):
    @authenticate_warp
    @cubes_warp
    def _read_cube_imp(user_name: str):
        return {
            JSON_STATUS_KEY: Statuses.SUCCESS,
            JSON_DESC_KEY: "cube read successfully.",
            JSON_CUBE_KEY: users_cubers_interfaces[user_name].read_cube()
        }

    return _read_cube_imp(user_name, hashed_password, user_name, user_name)


@app.put('/cubes/operation')
async def write_cube(user_name: str, hashed_password: str, cube_operation: str, request: Request):
    @authenticate_warp
    @cubes_warp
    def _write_cube_imp(user_name: str, cube_operation: str):
        return {
            JSON_STATUS_KEY: Statuses.SUCCESS,
            JSON_DESC_KEY: "cube write successfully.",
            JSON_CUBE_KEY: users_cubers_interfaces[user_name].write_cube(cube_operation)
        }

    return _write_cube_imp(user_name, hashed_password, user_name, user_name, cube_operation)


@app.delete('/cubes/delete')
async def delete_cube(user_name: str, hashed_password: str, request: Request):
    @authenticate_warp
    @cubes_warp
    def _delete_cube_imp(user_name: str):
        deleted_cube = users_cubers_interfaces[user_name].delete_cube()
        users_cubers_interfaces[user_name].select_cube()
        return {
            JSON_STATUS_KEY: Statuses.SUCCESS,
            JSON_DESC_KEY: "cube deleted successfully.",
            JSON_CUBE_KEY: deleted_cube
        }

    return _delete_cube_imp(user_name, hashed_password, user_name, user_name)


if __name__ == "__main__":
    uvicorn.run("API:app", host="0.0.0.0", port=37770, log_level="info")
