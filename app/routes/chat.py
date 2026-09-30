from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional, Any
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

@router.post("/chat")
def chat(payload: ChatMessage):

    user_id = payload.user_id
    message = payload.message.strip()

    if user_id not in sessions:

        sessions[user_id] = {
            "stage": "start"
        }

    stage = sessions[user_id]["stage"]

    # -------------------
    # START
    # -------------------

    if stage == "start":

        return chat_response(
            reply="Welcome to Product Upload AI. Upload a product image to begin.",
            stage="start",
            input_type="image"
        )

    # -------------------
    # COLORS
    # -------------------

    if stage == "waiting_for_colors":

        selected_colors = parse_colors(message)

        if not selected_colors:

            return chat_response(
                reply="Please select at least one color.",
                stage="waiting_for_colors",
                input_type="multi_select",
                options=get_colors(),
                field="colors"
            )

        sessions[user_id]["selected_colors"] = (
            selected_colors
        )

        sessions[user_id]["upload_color_index"] = 0

        sessions[user_id]["uploaded_images"] = {}

        sessions[user_id]["stage"] = (
            "waiting_for_color_image_upload"
        )

        return chat_response(
            reply=f"Upload image for {selected_colors[0]}",
            stage="waiting_for_color_image_upload",
            input_type="image",
            field=selected_colors[0]
        )

    if stage == "waiting_for_color_image_upload":

        colors = (
            sessions[user_id]
            ["selected_colors"]
        )

        index = (
            sessions[user_id]
            ["upload_color_index"]
        )

        current_color = colors[index]

        sessions[user_id][
            "uploaded_images"
        ][current_color] = message

        sessions[user_id][
            "upload_color_index"
        ] += 1

        next_index = (
            sessions[user_id]
            ["upload_color_index"]
        )

        if next_index < len(colors):

            next_color = colors[next_index]

            return chat_response(
                reply=f"Upload image for {next_color}",
                stage="waiting_for_color_image_upload",
                input_type="image",
                field=next_color
            )

        attributes = (
            sessions[user_id]
            ["draft_product"]
            ["attributes"]
        )

        if attributes:

            sessions[user_id]["attributes"] = (
                attributes
            )

            sessions[user_id]["attribute_names"] = (
                list(attributes.keys())
            )

            sessions[user_id]["attribute_index"] = 0

            sessions[user_id]["selected_attributes"] = {}

            sessions[user_id]["stage"] = (
                "waiting_for_attributes"
            )

            first_name = (
                sessions[user_id]
                ["attribute_names"][0]
            )

            options = attributes[first_name]

            return chat_response(
                reply=f"Choose a value for {first_name}",
                stage="waiting_for_attributes",
                input_type="single_select",
                options=options,
                field=first_name
            )

        sizes = (
            sessions[user_id]
            ["draft_product"]
            ["available_sizes"]
        )

        if sizes:

            sessions[user_id]["stage"] = (
                "waiting_for_sizes"
            )

            return chat_response(
                reply="Choose the available sizes.",
                stage="waiting_for_sizes",
                input_type="multi_select",
                options=sizes,
                field="sizes"
            )

        sessions[user_id]["stage"] = (
            "waiting_for_price"
        )

        return chat_response(
            reply="Enter the selling price.",
            stage="waiting_for_price",
            input_type="number",
            field="price"
        )

    # =====================================
    # ADD THE NEW BLOCK RIGHT HERE
    # =====================================

    if stage == "waiting_for_attributes":

        attribute_names = (
            sessions[user_id]
            ["attribute_names"]
        )

        index = (
            sessions[user_id]
            ["attribute_index"]
        )

        if index >= len(attribute_names):

            sizes = (
                sessions[user_id]
                ["draft_product"]
                ["available_sizes"]
            )

            if sizes:

                sessions[user_id]["stage"] = (
                    "waiting_for_sizes"
                )

                return chat_response(
                    reply="Choose the available sizes.",
                    stage="waiting_for_sizes",
                    input_type="multi_select",
                    options=sizes,
                    field="sizes"
                )

            sessions[user_id]["stage"] = (
                "waiting_for_price"
            )

            return chat_response(
                reply="Enter the selling price.",
                stage="waiting_for_price",
                input_type="number",
                field="price"
            )

        current_name = attribute_names[index]

        allowed_values = (
            sessions[user_id]
            ["attributes"]
            [current_name]
        )

        normalized_message = message.strip().lower()

        matched_value = next(
            (
                value
                for value in allowed_values
                if value.strip().lower()
                == normalized_message
            ),
            None
        )

        if matched_value is None:

            return chat_response(
                reply=f"Please choose a valid value for {current_name}.",
                stage="waiting_for_attributes",
                input_type="single_select",
                options=allowed_values,
                field=current_name
            )

        sessions[user_id][
            "selected_attributes"
        ][current_name] = matched_value

        sessions[user_id][
            "attribute_index"
        ] += 1

        next_index = (
            sessions[user_id]
            ["attribute_index"]
        )

        total = len(attribute_names)

        if next_index < total:

            next_name = attribute_names[next_index]

            options = (
                sessions[user_id]
                ["attributes"]
                [next_name]
            )

            return chat_response(
                reply=f"Choose a value for {next_name}.",
                stage="waiting_for_attributes",
                input_type="single_select",
                options=options,
                field=next_name
            )

        sizes = (
            sessions[user_id]
            ["draft_product"]
            ["available_sizes"]
        )

        if sizes:

            sessions[user_id]["stage"] = (
                "waiting_for_sizes"
            )

            return chat_response(
                reply="Choose the available sizes.",
                stage="waiting_for_sizes",
                input_type="multi_select",
                options=sizes,
                field="sizes"
            )

        sessions[user_id]["stage"] = (
            "waiting_for_price"
        )

        return chat_response(
            reply="Enter the selling price.",
            stage="waiting_for_price",
            input_type="number",
            field="price"
        )

    # -------------------
    # SIZES
    # -------------------

    if stage == "waiting_for_sizes":

        selected_sizes = [
            s.strip()
            for s in message.split(",")
            if s.strip()
        ]

        allowed_sizes = get_sizes()

        invalid = [
            s
            for s in selected_sizes
            if s not in allowed_sizes
        ]

        if invalid:

            return chat_response(
                reply=f"Invalid sizes: {', '.join(invalid)}",
                stage="waiting_for_sizes",
                input_type="multi_select",
                options=allowed_sizes,
                field="sizes"
            )

        sessions[user_id][
            "selected_sizes"
        ] = selected_sizes

        sessions[user_id]["stage"] = (
            "waiting_for_price"
        )

        return chat_response(
            reply="Enter the selling price.",
            stage="waiting_for_price",
            input_type="number",
            field="price"
        )

    # -------------------
    # PRICE
    # -------------------

    if stage == "waiting_for_price":

        try:

            price = float(message)

            if price <= 0:
                raise ValueError

            sessions[user_id]["price"] = price

        except ValueError:

            return chat_response(
                reply="Please enter a valid positive price.",
                stage="waiting_for_price",
                input_type="number",
                field="price"
            )

        sessions[user_id]["stage"] = (
            "waiting_for_stock"
        )

        return chat_response(
            reply="Enter stock quantity.",
            stage="waiting_for_stock",
            input_type="number",
            field="stock"
        )

    # -------------------
    # STOCK
    # -------------------

    if stage == "waiting_for_stock":

        try:

            stock = int(message)

            if stock < 0:
                raise ValueError

            sessions[user_id]["stock"] = stock

        except ValueError:

            return chat_response(
                reply="Please enter a valid stock quantity.",
                stage="waiting_for_stock",
                input_type="number",
                field="stock"
            )

        sessions[user_id]["stage"] = (
            "waiting_for_approval"
        )

        review = build_product_review(
            sessions[user_id]
        )

        return chat_response(
            reply="Please review the product before creating it.",
            stage="waiting_for_approval",
            input_type="approval",
            review=review
        )

    # -------------------
    # APPROVAL
    # -------------------

    if stage == "waiting_for_approval":

        if message.lower() != "yes":

            return {
                "reply":
                "Type YES to create product."
            }

        draft = sessions[user_id][
            "draft_product"
        ]

        colors = sessions[user_id][
            "selected_colors"
        ]

        sizes = sessions[user_id].get(
            "selected_sizes",
            []
        )

        price = sessions[user_id][
            "price"
        ]

        stock = sessions[user_id][
            "stock"
        ]

        product_id = save_product(
            title=draft["title"],
            description=draft["description"],
            classification=draft["classification"],
            selected_attributes=
                sessions[user_id].get(
                    "selected_attributes",
                    {}
                )
        )

        uploaded_images = sessions[user_id].get(
            "uploaded_images",
            {}
        )

        variant_images = []

        for color, image_path in uploaded_images.items():

            variant_images.append(
                {
                    "color": color,
                    "image_path": image_path
                }
            )

        if not variant_images:

            return chat_response(
                reply=(
                    "No variant images were found. "
                    "Please restart product creation."
                ),
                stage="waiting_for_approval"
            )

        for variant in variant_images:

            if not isinstance(
                variant,
                dict
            ):

                print(
                    "INVALID VARIANT:",
                    variant
                )

                continue

            color = variant.get(
                "color"
            )

            image_url = variant.get(
                "image_path"
            )

            if not color or not image_url:

                print(
                    "MISSING VARIANT DATA:",
                    variant
                )

                continue

            if sizes:

                for size in sizes:

                    save_variant(
                        product_id=product_id,
                        size=size,
                        color=color,
                        stock=stock,
                        price=price,
                        image_url=image_url
                    )

            else:

                save_variant(
                    product_id=product_id,
                    size="N/A",
                    color=color,
                    stock=stock,
                    price=price,
                    image_url=image_url
                )

        del sessions[user_id]

        return {
            "reply":
            f"""
    Product created successfully.

    Product ID:
    {product_id}

    Colors:
    {len(colors)}

    Sizes:
    {len(sizes)}

    Price:
    {price}

    Stock:
    {stock}

    Weight:
    {draft["estimated_weight"]["weight_kg"]} kg
    """
        }

    return {
        "reply":
        "Unknown state."
    }


@router.post("/chat/upload-image")
def chat_upload_image(
    payload: ChatImageUpload
):

    result = create_product_from_image(
        CreateProductRequest(
            title=payload.title,
            description=payload.description,
            image_path=payload.image_path
        )
    )

    classification = result["classification"]

    detected_color = result["detected_color"]

    sizes = result["available_sizes"]

    colors = result["available_colors"]

    dimensions = result["dimensions"]

    weight = result["estimated_weight"]

    attributes = result["attributes"]

    size_text = (
        ", ".join(sizes)
        if sizes
        else "Not Applicable"
    )

    if attributes:

        attribute_text = ""

        for name, values in attributes.items():

            attribute_text += (
                f"{name}: "
                f"{', '.join(values)}\n"
            )

    else:

        attribute_text = "Not Applicable"

    sessions[payload.user_id] = {
        "stage": "waiting_for_colors",
        "draft_product": result
    }

    reply = f"""
Product Analysis

Segment:
{classification['segment']}

Family:
{classification['family']}

Class:
{classification['class']}

Brick:
{classification['brick']}

Detected Color:
{detected_color}

Suggested Color:
{detected_color}

Size Class:
{dimensions["size_class"]}

Estimated Product Weight:
{weight["weight_kg"]} kg

Product Dimensions:
{dimensions["product_length_cm"]} x
{dimensions["product_width_cm"]} x
{dimensions["product_height_cm"]} cm

Shipping Dimensions:
{dimensions["shipping_length_cm"]} x
{dimensions["shipping_width_cm"]} x
{dimensions["shipping_height_cm"]} cm


Available Sizes:
{size_text}

Available Colors:
{", ".join(colors)}

Available Attributes:
{attribute_text}

Choose colors.

Detected color:
{detected_color}

Suggested:
{detected_color}

Example:
Black, White, Blue

Custom colors allowed.

"""

    sessions[payload.user_id] = {
        "stage": "waiting_for_colors",
        "draft_product": result,
        "surface_analysis": result["surface_analysis"],
        "selected_colors": [],
        "selected_attributes": {},
        "selected_sizes": []
    }

    return chat_response(
        reply=reply,
        stage="waiting_for_colors",
        input_type="multi_select",
        options=result["available_colors"],
        selected=[],
        field="colors"
    )

def build_product_review(session):

    draft = session["draft_product"]

    classification = draft["classification"]

    return {
        "title": draft["title"],

        "description": draft["description"],

        "classification": {
            "segment": classification.get("segment"),
            "family": classification.get("family"),
            "class": classification.get("class"),
            "brick": classification.get("brick")
        },

        "confidence": draft.get("confidence"),

        "detected_color": draft.get(
            "detected_color"
        ),

        "colors": session.get(
            "selected_colors",
            []
        ),

        "attributes": session.get(
            "selected_attributes",
            {}
        ),

        "sizes": session.get(
            "selected_sizes",
            []
        ),

        "price": session.get(
            "price"
        ),

        "stock": session.get(
            "stock"
        ),

        "dimensions": draft.get(
            "dimensions"
        ),

        "estimated_weight": draft.get(
            "estimated_weight"
        )
    }

def chat_response(
    reply: str,
    stage: str,
    input_type: str = "text",
    options: Optional[List[str]] = None,
    selected: Optional[List[str]] = None,
    field: Optional[str] = None,
    review: Optional[Dict[str, Any]] = None
):
    return {
        "reply": reply,
        "stage": stage,
        "input_type": input_type,
        "options": options or [],
        "selected": selected or [],
        "field": field,
        "review": review
    }

sessions = {}