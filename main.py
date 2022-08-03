import socket, time
import requests


def fn(func):
    def wrapper():
        print("stated")
        func()
        print("end")
    return wrapper


def ffn(func):
    def wrapper():
        print("begin")
        func()
        print("finish")
    return wrapper


@fn
@ffn
def f():
    print("in function")


if __name__ == '__main__':
    dct = {
        "a" : ";lkj",
        "b" : "asdgfd",
        "c" : "adljf"
    }

    print(list(dct.values())[0])



