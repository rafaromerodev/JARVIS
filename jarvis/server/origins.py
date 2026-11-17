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
"""

from __future__ import annotations

import re

LOOPBACK_ORIGIN_REGEX = r"^https?://(127\.0\.0\.1|localhost|\[::1\])(:\d{1,5})?$"
_LOOPBACK_ORIGIN = re.compile(LOOPBACK_ORIGIN_REGEX)


def is_allowed_origin(origin: str | None) -> bool:
    return origin is None or _LOOPBACK_ORIGIN.fullmatch(origin) is not None
