"""Origin checks for the local HTTP and WebSocket API.

The backend binds to loopback and exposes tools that act on the machine, so
the only browser pages allowed to talk to it are ones served from loopback
(the bundled UI, the Vite dev server, any custom ``--port``). A page on any
other site must not be able to drive it.

CORS alone is not enough: browsers still *send* "simple" cross-origin requests
(e.g. a form POST) and only hide the response, and WebSockets are not covered
by CORS at all. So foreign origins are rejected server-side as well.

Requests without an ``Origin`` header (curl, scripts, the Electron main
process) are allowed: browsers always attach ``Origin`` to cross-origin
requests and to every WebSocket handshake.

The ``Host`` header must also be a loopback name. Otherwise a DNS-rebinding
page (a public domain that re-resolves to 127.0.0.1) would be same-origin with
the API, send no ``Origin`` on GET requests, and be able to read responses.
"""

from __future__ import annotations

import re

LOOPBACK_ORIGIN_REGEX = r"^https?://(127\.0\.0\.1|localhost|\[::1\])(:\d{1,5})?$"
_LOOPBACK_ORIGIN = re.compile(LOOPBACK_ORIGIN_REGEX)
_LOOPBACK_HOST = re.compile(r"^(127\.0\.0\.1|localhost|\[::1\])(:\d{1,5})?$")


def is_allowed_origin(origin: str | None) -> bool:
    return origin is None or _LOOPBACK_ORIGIN.fullmatch(origin) is not None


def is_allowed_host(host: str | None) -> bool:
    return host is not None and _LOOPBACK_HOST.fullmatch(host.lower()) is not None
