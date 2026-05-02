from fastapi import Response


class NoContentResponse(Response):
    def __init__(self):
        super().__init__(status_code=204)
