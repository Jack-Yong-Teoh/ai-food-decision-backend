from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class HTTPBearer401(HTTPBearer):
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        try:
            return await super().__call__(request)
        except HTTPException as exc:
            # Convert 403 Forbidden to 401 Unauthorized if it's due to missing/invalid auth
            if exc.status_code == status.HTTP_403_FORBIDDEN:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from exc
            raise
