from aiohttp.web import run_app

from .main import init_app

if __name__ == "__main__":
    run_app(init_app())
