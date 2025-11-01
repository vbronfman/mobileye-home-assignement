# def hello() -> str:
#     return "Hello from gitlab-calls!"

from .gitlab_calls import *
#from .gitlab_calls import grant_user_role, get_items_by_year

__all__ = ["bogus", "grant_user_role", "get_items_by_year"]
