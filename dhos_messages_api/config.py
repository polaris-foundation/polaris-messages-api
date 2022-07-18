from flask import Flask


class Configuration:
    pass


def init_config(app: Flask) -> None:
    app.config.from_object(Configuration)
