from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
from config import get_settings
from sqlalchemy.orm import Session
from database import get_db
from models import User

settings = get_settings()
security = HTTPBearer()

# Clerk JWKS endpoint
CLERK_JWKS_URL = f"https://{settings.clerk_publishable_key.split('_')[1]}.clerk.accounts.dev/.well-known/jwks.json"


class AuthService:
    def __init__(self):
        self.jwks_client = None

    def _get_jwks_client(self):
        if self.jwks_client is None:
            # Extract the Clerk frontend API from publishable key
            # Format: pk_test_xxxx or pk_live_xxxx
            self.jwks_client = PyJWKClient(CLERK_JWKS_URL)
        return self.jwks_client

    def verify_token(self, token: str) -> dict:
        """Verify a Clerk JWT token and return the payload."""
        try:
            jwks_client = self._get_jwks_client()
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user.
    Creates the user in DB if they don't exist.
    """
    token = credentials.credentials
    payload = auth_service.verify_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Get or create user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(
            id=user_id,
            email=payload.get("email"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
