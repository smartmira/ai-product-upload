import os
import time
import json
from fastapi import APIRouter, HTTPException
from app.ai.image_analyzer import (
        analyze_image_once
    )

from app.services.cloudinary_service import (
    upload_product_image
)

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
    tags=["Products"]
)

@router.post("/save-product")
def save_product_endpoint(payload: ProductRequest):

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

    product_id = save_product(
        title=payload.title,
        description=payload.description,
        classification=classification,
        selected_attributes=payload.selected_attributes
    )

    return {
        "success": True,
        "product_id": product_id,
        "selected_attributes": payload.selected_attributes
    }

@router.post("/create-product-from-image")
def create_product_from_image(
    payload: CreateProductRequest
):

    total_start = time.time()

    filename, _ = os.path.splitext(payload.image_path)
    nobg_path = f"{filename}_nobg.png"

    # -------------------------
    # Background Removal
    # -------------------------
    t = time.time()

    remove_background(
        payload.image_path,
        nobg_path
    )

    print(
        f"remove_background: "
        f"{round(time.time() - t, 2)} sec"
    )

    cloudinary_result = upload_product_image(
        nobg_path
    )

    image_url = cloudinary_result["url"]

    public_id = cloudinary_result["public_id"]

    print("\nCLOUDINARY URL:")
    print(image_url)

    print("\nCLOUDINARY PUBLIC ID:")
    print(public_id)

    t = time.time()

    analysis = analyze_image_once(
        nobg_path
    )

    surface_analysis = analysis["surface_analysis"]

    visual_features = analysis["visual_features"]

    print(
            f"surface_analysis: "
            f"{round(time.time() - t, 2)} sec"
        )

    print(
                f"visual_features: "
                f"{round(time.time() - t, 2)} sec"
            )

    print(
            f"image_description: "
            f"{round(time.time() - t, 2)} sec"
        )
    
    print("VISUAL FEATURES:")
    print(visual_features)

    print("SURFACE ANALYSIS:")
    print(surface_analysis)

    taxonomy_search_description = analysis.get(
        "taxonomy_search_description",
        ""
    )
    # -------------------------
    # Color Detection
    # -------------------------
    t = time.time()

    color_result = detect_color(
        nobg_path
    )

    print(
        f"detect_color: "
        f"{round(time.time() - t, 2)} sec"
    )

    product_text = f"""
    Title:
    {payload.title}

    Description:
    {payload.description}

    Visual Product Type:
    {visual_features.get("product_type","")}

    Primary Usage:
    {visual_features.get("usage","")}

    Material:
    {visual_features.get("material","")}

    Construction:
    {visual_features.get("construction","")}

    Size:
    {visual_features.get("size_category","")}

    Taxonomy_description:
    {taxonomy_search_description}
    """

    taxonomy_hint = ""

    if visual_features.get("product_type"):
        taxonomy_hint += (
            f"This product is a "
            f"{visual_features['product_type']}.\n"
        )

    if visual_features.get("usage"):
        taxonomy_hint += (
            f"It is used for "
            f"{visual_features['usage']}.\n"
        )

    product_text += "\n" + taxonomy_hint

    print("\nPRODUCT TEXT SENT TO EMBEDDINGS")
    print(product_text)

    t = time.time()

    matches = find_matches(
        product_text,
        k=5
    )

    print(
        f"taxonomy_matcher: "
        f"{round(time.time() - t, 2)} sec"
    )

    t = time.time()

    classification = classify_product(
        product_text,
        matches
    )

    print(
        f"classify_product: "
        f"{round(time.time() - t, 2)} sec"
    )

    attributes = get_attribute_values(
        classification["brick"]
    )

    available_colors = get_colors()

    brick_name = classification["brick"]

    available_sizes = get_sizes(
        brick_name
    )

    print(attributes)

    print("BEFORE DIMENSIONS")


    t = time.time()

    dimensions = estimate_dimensions(
        title=payload.title,
        description=payload.description,
        classification=classification,
        visual_features=visual_features,
        surface_analysis=surface_analysis,
    )

    print(
        f"estimate_dimensions: "
        f"{round(time.time() - t, 2)} sec"
    )

    confidence = 0.0

    if matches:

        best_distance = matches[0]["distance"]

        if len(matches) == 1:

            confidence = round(
                max(
                    0.0,
                    min(
                        1.0,
                        1 - (best_distance / 3)
                    )
                ),
                2
            )

        else:

            second_distance = matches[1]["distance"]

            gap = second_distance - best_distance

            distance_score = max(
                0.0,
                min(
                    1.0,
                    1 - (best_distance / 3)
                )
            )

            gap_score = max(
                0.0,
                min(
                    1.0,
                    gap * 5
                )
            )

            confidence = round(
                (
                    distance_score * 0.6
                    +
                    gap_score * 0.4
                ),
                2
            )

    print("\nTOP TAXONOMY MATCHES")

    for m in matches:
        print(
            f"{m['brick']} -> "
            f"{round(m['distance'], 4)}"
    )

    weight = {
        "weight_kg":
            dimensions["product_weight_kg"]
    }

    print("QWEN ANALYSIS:")
    print(surface_analysis)
    print(
        f"TOTAL ANALYSIS TIME: "
        f"{round(time.time() - total_start, 2)} sec"
    )

    try:

        if os.path.exists(payload.image_path):
            os.remove(payload.image_path)

        if os.path.exists(nobg_path):
            os.remove(nobg_path)

        print("\nLOCAL FILES DELETED")

    except Exception as e:

        print("\nDELETE ERROR:")
        print(e)

    print("\nDIMENSIONS SENT TO UI:")
    print(json.dumps(dimensions, indent=2))

    return {
        "success": True,
        "title": payload.title,
        "description": payload.description,
        "classification": classification,
        "visual_features": visual_features,
        "detected_color": color_result["detected_color"],
        "available_sizes": available_sizes,
        "available_colors": available_colors,
        "confidence": confidence,
        "candidate_bricks": [
            m["brick"]
            for m in matches
        ],
        "attributes": attributes,

        "dimensions": dimensions,

        "estimated_weight": weight,

        "size_class":
            dimensions["size_class"],

        "background_removed_image": image_url,
        "image_public_id": public_id,

        "surface_analysis": surface_analysis
    }