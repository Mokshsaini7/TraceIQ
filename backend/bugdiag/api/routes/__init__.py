"""API routes package.
"""

from bugdiag.api.routes.health import router as health_router
from bugdiag.api.routes.submissions import router as submissions_router
from bugdiag.api.routes.diagnosis import router as diagnosis_router
from bugdiag.api.routes.knowledge_base import router as knowledge_router
from bugdiag.api.routes.search import router as search_router
from bugdiag.api.routes.system import router as system_router
from bugdiag.api.routes.stats import router as stats_router

__all__ = [
    "health_router",
    "submissions_router",
    "diagnosis_router",
    "knowledge_router",
    "search_router",
    "system_router",
    "stats_router"
]
