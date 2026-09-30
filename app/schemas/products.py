from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class ProductRequest(BaseModel):
    title: str
    description: str = ""
    selected_attributes: Dict[str, str] = Field(
        default_factory=dict
    )


class VariantRequest(BaseModel):
    product_id: int
    size: str
    color: str
    stock: int
    price: float
    image_url: str = ""


class BulkVariantRequest(BaseModel):
    product_id: int
    sizes: List[str]
    colors: List[str]
    stock: int
    price: float
    image_url: str = ""


class CreateProductRequest(BaseModel):
    title: str
    description: str = ""
    image_path: str


class ProductImageRequest(BaseModel):
    product_id: int
    image_url: str


class ColorDetectionRequest(BaseModel):
    image_path: str


class ChatMessage(BaseModel):
    user_id: str
    message: str


class ChatImageUpload(BaseModel):
    user_id: str
    title: str
    description: str = ""
    image_path: str

class ChatResponse(BaseModel):
    reply: str
    stage: str
    input_type: str = "text"
    options: List[str] = Field(default_factory=list)
    selected: List[str] = Field(default_factory=list)
    field: Optional[str] = None
    review: Optional[Dict[str, Any]] = None

