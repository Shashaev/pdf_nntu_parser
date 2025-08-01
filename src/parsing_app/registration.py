import typing

import schemes


__all__ = []

registered_functions: list[schemes.CalledFunction] = []


def run(
    max_count: int = 1, delay_time: float = 0, endless_execution: bool = False,
):
    def inner(fun: typing.Callable):
        if max_count != 1 and endless_execution:
            raise ValueError

        if max_count != 0:
            called_fun = schemes.CalledFunction(
                max_count=max_count,
                delay_time=delay_time,
                endless_execution=endless_execution,
                fun=fun,
            )
            registered_functions.append(called_fun)

        return fun

    return inner
