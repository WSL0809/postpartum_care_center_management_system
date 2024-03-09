from functools import wraps
from sqlalchemy.exc import SQLAlchemyError


def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            # 这里处理 SQLAlchemy 相关的异常
            print(f"Database error occurred: {e}")
            # 可以选择重新抛出异常或返回一个错误信息
            raise
        except Exception as e:
            # 处理其他异常
            print(f"An error occurred: {e}")
            raise

    return wrapper
