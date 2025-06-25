
from .exception import ArgumentException, RuntimeException

def val_arg(value, message):
    if not value:
        raise ArgumentException(message)

def val_run(value, message):
    if not value:
        raise RuntimeException(message)
