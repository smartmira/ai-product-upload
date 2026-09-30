from fastapi import APIRouter, HTTPException
from fastapi import UploadFile, File
import os
import psycopg2
import shutil

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
    tags=["Images"]
)

from uuid import uuid4

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

@router.post("/upload-image")
def upload_image(payload: ProductImageRequest):

    conn = psycopg2.connect(
        host="localhost",
        database="marketplace_taxonomy",
        user="postgres",
        password="SMirac_5555"
    )

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO product_images(
            product_id,
            image_url
        )
        VALUES (%s,%s)
    """, (
        payload.product_id,
        payload.image_url
    ))

    conn.commit()
    conn.close()

    return {
        "success": True
    }


@router.post("/upload-product-image")
async def upload_product_image(
    file: UploadFile = File(...)
):

    if file.content_type not in ALLOWED_IMAGE_TYPES:

        return {
            "success": False,
            "error": "Only JPG, PNG and WEBP images are allowed."
        }

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    extension = os.path.splitext(
        file.filename or ""
    )[1].lower()

    filename = (
        f"{uuid4()}{extension}"
    )

    filepath = os.path.join(
        "uploads",
        filename
    )

    with open(filepath, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {
        "success": True,
        "filepath": filepath
    }

@router.post("/detect-color")
def detect_product_color(
    payload: ColorDetectionRequest
):

    return detect_color(
        payload.image_path
    )

@router.post("/remove-background")
def remove_bg(
    payload: ColorDetectionRequest
):

    import os

    filename, ext = os.path.splitext(
        payload.image_path
    )

    output_path = f"{filename}_nobg.png"

    remove_background(
        payload.image_path,
        output_path
    )

    return {
        "output_path": output_path
    }

@router.get("/product-images/{product_id}")
def product_images(product_id: int):

    return {
        "product_id": product_id,
        "images": get_product_images(product_id)
    }