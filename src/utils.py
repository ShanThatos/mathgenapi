from typing import Optional


def require_not_none[T](value: Optional[T]) -> T:
    if value is None:
        raise ValueError("Unexpected None value")
    return value


def on_startup(*args, **kwargs):
    def decorator(f):
        f(*args, **kwargs)
        return f

    return decorator
