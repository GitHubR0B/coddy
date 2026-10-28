# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
# ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
# ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
# ║                                                                  ║
# ║            © 2026 CodeX Devs — All Rights Reserved              ║
# ║                                                                  ║
# ║   discord  ──  https://discord.gg/codexdev                      ║
# ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
# ║   github   ──  https://github.com/RayExo                        ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import os
from typing import Optional, TYPE_CHECKING
from fastapi import HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from slowapi import Limiter
from slowapi.util import get_remote_address

if TYPE_CHECKING:
    from core.zyrox import zyrox

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["1000 per minute"])

# Global reference to the bot instance
_bot_instance: Optional["zyrox"] = None

# Security scheme
# auto_error=False para poder devolver un mensaje propio (en español) en lugar
# del "Not authenticated" por defecto de FastAPI.
security = HTTPBearer(auto_error=False)

def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)):
    """
    Dependency to verify the API key from the Authorization header.
    Expected: Authorization: Bearer <API_KEY>
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="No autenticado. Falta la cabecera 'Authorization: Bearer <API_KEY>'."
        )

    api_key = os.getenv("DASHBOARD_API_KEY")
    
    # If no key is set in env, we might want to allow for local testing or force it.
    # The requirement says "Read API key from environment variable", implying it's required.
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="La variable de entorno DASHBOARD_API_KEY no está configurada."
        )

    if credentials.credentials != api_key:
        raise HTTPException(
            status_code=401,
            detail="Clave de API inválida o ausente."
        )
    return credentials.credentials

def set_bot(bot_instance: "zyrox"):
    """
    Sets the global bot instance. 
    This should be called in CodeX.py during startup.
    """
    global _bot_instance
    _bot_instance = bot_instance

def get_bot() -> "zyrox":
    """
    FastAPI dependency to retrieve the Discord bot instance.
    Usage: bot: zyrox = Depends(get_bot)
    """
    if _bot_instance is None:
        raise HTTPException(
            status_code=503, 
            detail="La instancia del bot de Discord aún no está inicializada."
        )
    return _bot_instance
