import logging

from aiohttp import web

from conduit.container import create_app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(create_app())
