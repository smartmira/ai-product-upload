from fastapi import FastAPI

from app.routes.products import router as products_router
from app.routes.variants import router as variants_router
from app.routes.images import router as images_router
from app.routes.classification import router as classification_router
from app.routes.chat import router as chat_router

app = FastAPI()

app.include_router(products_router)
app.include_router(variants_router)
app.include_router(images_router)
app.include_router(classification_router)
app.include_router(chat_router)