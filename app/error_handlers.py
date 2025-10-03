"""Module de gestion centralisée des erreurs HTTP.

Ce module enregistre les gestionnaires d'exceptions personnalisés pour l'application FastAPI afin d'uniformiser les réponses d'erreur et améliorer la gestion des exceptions.

Example:
    >>> from app.error_handlers import register_error_handlers
    >>> register_error_handlers(app)
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Enregistre les gestionnaires d'exceptions pour l'application FastAPI.

    Configure des handlers personnalisés pour capturer et formater les erreurs HTTP et les exceptions générales, assurant des réponses JSON cohérentes.

    Args:
        app (FastAPI): Instance de l'application FastAPI

    Note:
        Les erreurs générales (Exception) sont loggées mais retournent un message générique pour éviter d'exposer des détails sensibles.
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Gestionnaire pour les exceptions HTTP (4xx, 5xx).

        Args:
            request (Request): Requête HTTP qui a causé l'erreur exc (StarletteHTTPException): Exception HTTP levée

        Returns:
            JSONResponse: Réponse JSON avec le code d'erreur et le détail
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Gestionnaire pour toutes les exceptions non gérées.

        Capture les erreurs inattendues, les logue et retourne une réponse générique pour ne pas exposer de détails techniques au client.

        Args:
            request (Request): Requête HTTP qui a causé l'erreur
            exc (Exception): Exception non gérée

        Returns:
            JSONResponse: Réponse JSON avec un code 500 et message générique
        """
        logger.error(f"Erreur non gérée: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Erreur interne du serveur"}
        )
