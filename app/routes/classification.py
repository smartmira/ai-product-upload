from fastapi import APIRouter, HTTPException
import json
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
    tags=["Classification"]
)

@router.post("/classify")
def classify(payload: ProductRequest):

    product_text = f"""
    {payload.title}

    {payload.description}
    """

    matches = find_matches(
        product_text,
        k=5
    )

    classification = classify_product(
        product_text,
        matches
    )

    attributes = get_attribute_values(
        classification["brick"]
    )

    print(json.dumps(attributes, indent=2))

    suggested_attributes = extract_attributes(
        product_text,
        attributes
    )

    candidate_bricks = [
        m["brick"]
        for m in matches
    ]

    confidence = 0.0

    if matches:
        confidence = round(
            1 / (1 + matches[0]["distance"]),
            2
        )

    return {
        "success": True,
        "classification": classification,
        "confidence": confidence,
        "candidate_bricks": candidate_bricks,
        "attributes": attributes,
        "suggested_attributes": suggested_attributes,
        "selected_attributes": payload.selected_attributes
    }

@router.post("/suggest-variants")
def suggest_variants(payload: ProductRequest):

    product_text = f"""
{payload.title}

{payload.description}
"""

    sizes = get_sizes()

    colors = get_colors()

    suggestions = suggest_sizes_and_colors(
        product_text,
        sizes,
        colors
    )

    return {
        "suggested_sizes":
            suggestions["suggested_sizes"],

        "suggested_colors":
            suggestions["suggested_colors"],

        "available_sizes":
            sizes,

        "available_colors":
            colors
    }

@router.post("/estimate-dimensions")
def estimate(payload: ProductRequest):

    product_text = f"""
    {payload.title}

    {payload.description}
    """

    matches = find_matches(
        product_text,
        k=5
    )

    classification = classify_product(
        product_text,
        matches
    )

    return estimate_dimensions(
        title=payload.title,
        description=payload.description,
        classification=classification,
        image_path=None,
        surface_analysis=None
    )