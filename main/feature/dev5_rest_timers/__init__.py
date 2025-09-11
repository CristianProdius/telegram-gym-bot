from aiogram import Router
from .handlers import router as handlers_router
from .plan import router as plan_router

router = Router()
router.include_router(handlers_router)
router.include_router(plan_router)

__all__ = ["router"]