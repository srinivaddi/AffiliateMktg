from starlette.responses import JSONResponse
import json


class PrettyJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(content, indent=4, ensure_ascii=False).encode("utf-8")


class GetJSONResponseData:
    """Helper to parse an existing Response and expose .body as decoded dict."""

    def __init__(self, response):
        self.body = json.loads(response.body.decode("utf-8"))
