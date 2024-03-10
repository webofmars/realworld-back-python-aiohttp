import typing as t

import structlog
from aiohttp import web
from structlog.typing import EventDict

from conduit.api.middlewares import REQUEST_ID_VAR
from conduit.container import create_app


def add_request_id_to_logs(_: t.Any, __: t.Any, event_dict: EventDict) -> EventDict:
    request_id = REQUEST_ID_VAR.get()
    if request_id is not None:
        event_dict["request_id"] = request_id
    return event_dict


if __name__ == "__main__":
    structlog.configure(
        processors=[
            add_request_id_to_logs,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.dict_tracebacks,
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
            structlog.processors.JSONRenderer(),
        ]
    )
    web.run_app(create_app())
