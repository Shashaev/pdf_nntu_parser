import fastapi

import api.anothe
import api.educational_plan
import api.rpd


main_router = fastapi.APIRouter()
main_router.include_router(api.educational_plan.router)
main_router.include_router(api.anothe.router)
main_router.include_router(api.rpd.router)
