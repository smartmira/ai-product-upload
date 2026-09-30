from fastapi import APIRouter, HTTPException
from app.schemas.products import (
    ProductRequest,
    VariantRequest,
    BulkVariantRequest,
    CreateProductRequest,
    ProductImageRequest,
    ColorDetectionRequest,
    ChatMessage,
    ChatImageUpload,
    ChatResponse,
)

router = APIRouter()

from app.dependencies import (
    estimate_dimensions,
    estimate_weight_ai,
    suggest_sizes_and_colors,
    extract_attributes,
    classify_product,
    detect_color,
    analyze_product_image,
    extract_visual_features,
    find_matches,
    get_attribute_values,
    save_product,
    save_variant,
    save_variants,
    get_product_variants,
    get_product_images,
    get_sizes,
    get_colors,
    remove_background,
)

from fastapi import APIRouter
router = APIRouter(
    prefix="",
    tags=["Variants"]
)

@router.post("/add-variant")
def add_variant(payload: VariantRequest):

    save_variant(
        product_id=payload.product_id,
        size=payload.size,
        color=payload.color,
        stock=payload.stock,
        price=payload.price,
        image_url=payload.image_url
    )

    return {
        "success": True
    }

@router.post("/add-variants")
def add_variants(payload: BulkVariantRequest):

    save_variants(
        product_id=payload.product_id,
        sizes=payload.sizes,
        colors=payload.colors,
        stock=payload.stock,
        price=payload.price,
        image_url=payload.image_url
    )

    return {
        "success": True,
        "variants_created":
            len(payload.sizes) * len(payload.colors)
    }


@router.get("/product-variants/{product_id}")
def product_variants(product_id: int):

    return {
        "product_id": product_id,
        "variants": get_product_variants(product_id)
    }