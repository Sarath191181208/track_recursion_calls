from functools import cache
from decorator import track_calls, write_to_file

@track_calls
@cache
def fib(n):
    if n <= 1:
        return 1
    return fib(n - 1) + fib(n-2)

print(fib(500))

write_to_file()
