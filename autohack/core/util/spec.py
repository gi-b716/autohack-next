from typing import Callable
import inspect


def getFunctionInfo(func: Callable) -> tuple[list[type], type]:
    sig = inspect.signature(func)
    params = sig.parameters
    paramTypes = [param.annotation for param in params.values()]
    return (paramTypes, sig.return_annotation)
