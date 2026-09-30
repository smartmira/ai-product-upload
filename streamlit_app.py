import os
import requests
import streamlit as st
import uuid
from app.db.get_sizes import get_sizes

def is_footwear(brick_name):

    if not brick_name:
        return False

    brick = brick_name.lower()

    keywords = [
        "footwear",
        "shoe",
        "shoes",
        "boot",
        "boots",
        "sneaker",
        "sneakers"
    ]

    return any(
        keyword in brick
        for keyword in keywords
    )



MEN_EU_SHOE_SIZES = [
    "39", "40", "41", "42", "43",
    "44", "45", "46", "47", "48"
]

WOMEN_EU_SHOE_SIZES = [
    "35", "36", "37", "38",
    "39", "40", "41", "42"
]

KIDS_SHOE_SIZES = [
    "19", "20", "21", "22", "23",
    "24", "25", "26", "27", "28",
    "29", "30", "31", "32", "33",
    "34", "35", "36", "37", "38"
]

st.set_page_config(
    page_title="AI Product Upload Assistant",
    layout="wide"
)

st.title("AI Product Upload Assistant")
if st.button("Clear Analysis Cache"):

    if "analysis" in st.session_state:

        del st.session_state["analysis"]

    st.rerun()
# --------------------------------------------------
# PRODUCT DETAILS
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload Product Image",
    type=["jpg", "jpeg", "png", "webp"]
)

title = st.text_input(
    "Product Name"
)

description = st.text_area(
    "Description"
)

price = st.number_input(
    "Price",
    min_value=0.0
)

stock = st.number_input(
    "Stock",
    min_value=0
)

# --------------------------------------------------
# ANALYZE PRODUCT
# --------------------------------------------------

if st.button("Analyze Product"):

    if uploaded_file is None:

        st.error(
            "Please upload a product image."
        )
        st.stop()

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    unique_filename = (
        f"{uuid.uuid4()}_{uploaded_file.name}"
    )

    filepath = os.path.join(
        "uploads",
        unique_filename
    )

    with open(filepath, "wb") as f:

        f.write(
            uploaded_file.read()
        )

    payload = {
        "title": title,
        "description": description,
        "image_path": filepath
    }

    print("\n===== PAYLOAD =====")
    print(payload)

    try:

        response = requests.post(
            "http://127.0.0.1:8000/create-product-from-image",
            json=payload,
            timeout=900
        )

    except Exception as e:

        st.error(f"Request Failed: {e}")

        print("\nREQUEST FAILED")
        print(e)

        st.stop()

    print("\n===== STATUS CODE =====")
    print(response.status_code)

    if response.status_code != 200:

        print("\n===== API ERROR =====")
        print(response.text)

        st.error(
            f"API Error: {response.text}"
        )

        st.stop()

    api_result = response.json()
    print("\n===== API TITLE =====")
    print(api_result.get("title"))

    print("\n===== API BRICK =====")
    print(
        api_result.get(
            "classification",
            {}
        ).get("brick")
    )

    print("\n===== API ATTRIBUTES =====")
    print(
        api_result.get(
            "attributes",
            {}
        )
    )
    print("\n===== PRODUCT RETURNED FROM API =====")
    print(api_result.get("title"))

    print(
        api_result.get(
            "classification",
            {}
        ).get("brick")
    )

    print("\n===== API RESPONSE =====")
    print(api_result)

    print("\n===== BEFORE UPDATE =====")
    print(st.session_state.get("analysis"))

    st.session_state["analysis"] = api_result

    print("\n===== AFTER UPDATE =====")
    print(st.session_state["analysis"])

    print("\n===== SESSION TITLE =====")
    print(
        st.session_state["analysis"].get(
            "title"
        )
    )

    print("\n====================")
    print("ANALYZE BUTTON CLICKED")
    print("TITLE:", title)
    print("FILE:", filepath)
    print("====================\n")

# --------------------------------------------------
# DISPLAY ANALYSIS
# --------------------------------------------------

if "analysis" in st.session_state:

    result = st.session_state["analysis"]

    st.write(
        "Analysis Time:",
        st.session_state.get(
            "analysis_time"
        )
    )

    st.write(
        "Session Title:",
        result.get("title")
    )

    st.write(
        "Session Brick:",
        result.get(
            "classification",
            {}
        ).get("brick")
    )

    st.write("DEBUG TITLE:")
    st.write(result.get("title"))

    st.write("DEBUG BRICK:")
    st.write(
        result.get(
            "classification",
            {}
        ).get(
            "brick"
        )
    )

    classification = result.get(
        "classification",
        {}
    )

    confidence = result.get(
        "confidence",
        0
    )

    st.subheader(
        "AI Analysis"
    )

    st.metric(
        "Classification Confidence",
        f"{confidence:.0%}"
    )

    # --------------------------------------------------
    # LOW CONFIDENCE WARNING
    # --------------------------------------------------

    if confidence < 0.60:

        st.warning(
            "Classification confidence is low."
        )

        candidate_bricks = result.get(
            "candidate_bricks",
            []
        )

        if candidate_bricks:

            st.subheader(
                "Alternative Categories"
            )

            for brick in candidate_bricks:

                st.write(
                    f"• {brick}"
                )

    # --------------------------------------------------
    # CATEGORY DISPLAY
    # --------------------------------------------------

    st.subheader(
        "Detected Category"
    )

    st.write(
        f"Segment: {classification.get('segment', '')}"
    )

    st.write(
        f"Family: {classification.get('family', '')}"
    )

    st.write(
        f"Class: {classification.get('class', '')}"
    )

    st.write(
        f"Brick: {classification.get('brick', '')}"
    )

    approve_category = st.radio(
        "Do you agree with this category?",
        [
            "Yes",
            "Choose Another"
        ]
    )

    selected_brick = (
        classification.get(
            "brick",
            ""
        )
    )

    if approve_category == "Choose Another":

        candidate_bricks = result.get(
            "candidate_bricks",
            []
        )

        if candidate_bricks:

            selected_brick = st.selectbox(
                "Select Category",
                candidate_bricks
            )

    footwear_type = None

    if is_footwear(selected_brick):

        st.subheader("Footwear Type")

        footwear_type = st.radio(
            "Select Footwear Audience",
            [
                "Men",
                "Women",
                "Kids",
                "Unisex"
            ]
        )

    # --------------------------------------------------
    # COLOR APPROVAL
    # --------------------------------------------------

    st.subheader(
        "Detected Color"
    )

    detected_color = result.get(
        "detected_color",
        ""
    )

    approve_color = st.radio(
        f"AI detected: {detected_color}",
        [
            "Approve",
            "Choose Another"
        ]
    )

    if approve_color == "Approve":

        selected_colors = [
            detected_color
        ]

    else:

        selected_colors = st.multiselect(
            "Select Colors",
            result.get(
                "available_colors",
                []
            )
        )

    # --------------------------------------------------
    # COLOR VARIANT IMAGES
    # --------------------------------------------------

    variant_images = {}
    uploaded_count = 0

    if selected_colors:

        st.subheader(
            "Upload Color Variant Images"
        )

        for color in selected_colors:

            uploaded_variant = st.file_uploader(
                f"Upload image for {color}",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ],
                key=f"variant_{color}"
            )

            if uploaded_variant:

                variant_images[
                    color
                ] = uploaded_variant

        uploaded_count = (
            len(variant_images)
        )

    st.info(
        f"{uploaded_count} of "
        f"{len(selected_colors)} "
        f"color images uploaded"
    )

    # --------------------------------------------------
    # WEIGHT
    # --------------------------------------------------

    st.subheader(
        "Weight"
    )

    estimated_weight = (
        result.get(
            "estimated_weight",
            {}
        ).get(
            "weight_kg",
            0
        )
    )

    weight = st.number_input(
        "Weight (kg)",
        value=float(
            estimated_weight
        )
    )

    # --------------------------------------------------
    # DIMENSIONS
    # --------------------------------------------------

    st.subheader("Dimensions")

    dimensions = result.get(
        "dimensions",
        {}
    )

    length = st.number_input(
        "Length (cm)",
        value=float(
            dimensions.get(
                "product_length_cm",
                0
            )
        )
    )

    width = st.number_input(
        "Width (cm)",
        value=float(
            dimensions.get(
                "product_width_cm",
                0
            )
        )
    )

    height = st.number_input(
        "Height (cm)",
        value=float(
            dimensions.get(
                "product_height_cm",
                0
            )
        )
    )

    shipping_length = st.number_input(
        "Shipping Length (cm)",
        value=float(
            dimensions.get(
                "shipping_length_cm",
                0
            )
        )
    )

    shipping_width = st.number_input(
        "Shipping Width (cm)",
        value=float(
            dimensions.get(
                "shipping_width_cm",
                0
            )
        )
    )

    shipping_height = st.number_input(
        "Shipping Height (cm)",
        value=float(
            dimensions.get(
                "shipping_height_cm",
                0
            )
        )
    )

    fragile = st.radio(
        "Fragile Product?",
        ["Yes", "No"],
        key="fragile_ai",
        index=(
            0
            if dimensions.get(
                "fragile",
                False
            )
            else 1
        )
    )

    st.caption(
        f"AI Confidence: "
        f"{dimensions.get('confidence',0):.0%}"
    )


    # --------------------------------------------------
    # ATTRIBUTES
    # --------------------------------------------------

    st.subheader(
        "Attributes"
    )

    attributes = result.get(
        "attributes",
        {}
    )

    print(result)

    print("ATTRIBUTES TYPE:")
    print(type(attributes))

    print("ATTRIBUTES VALUE:")
    print(attributes)

    selected_attributes = {}

    selected_attributes = {}

    for name, values in attributes.items():

        selected_attributes[name] = st.selectbox(
            name,
            values
        )

    # --------------------------------------------------
    # SIZES
    # --------------------------------------------------

    selected_sizes = []

    if is_footwear(selected_brick):

        if footwear_type == "Men":

            available_sizes = MEN_EU_SHOE_SIZES

        elif footwear_type == "Women":

            available_sizes = WOMEN_EU_SHOE_SIZES

        elif footwear_type == "Kids":

            available_sizes = KIDS_SHOE_SIZES

        else:

            available_sizes = sorted(
                set(
                    MEN_EU_SHOE_SIZES
                    + WOMEN_EU_SHOE_SIZES
                ),
                key=lambda x: int(x)
            )

    else:

        available_sizes = get_sizes(
            selected_brick
        )

    if available_sizes:

        st.subheader("Sizes")

        selected_sizes = st.multiselect(
            "Select Sizes",
            available_sizes
        )

    # --------------------------------------------------
    # REVIEW
    # --------------------------------------------------

    st.subheader("Review Product")

    st.write(f"**Category:** {selected_brick}")
    st.write(f"**Colors:** {', '.join(selected_colors)}")

    if selected_sizes:
        st.write(f"**Sizes:** {', '.join(selected_sizes)}")

    st.write(f"**Price:** ₦{price:,.0f}")
    st.write(f"**Stock:** {stock}")

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    if not selected_colors:

        st.error(
            "Please select at least one color."
        )

    else:

        all_uploaded = (
            len(variant_images)
            == len(selected_colors)
        )

        # --------------------------------------------------
        # CREATE PRODUCT
        # --------------------------------------------------

        if st.button(
            "Create Product"
        ):

            if not all_uploaded:

                st.error(
                    "Please upload images for all selected colors."
                )
                st.stop()

            save_response = requests.post(
                "http://127.0.0.1:8000/save-product",
                json={
                    "title": title,
                    "description": description,
                    "selected_attributes":
                        selected_attributes,
                    "selected_category":
                        selected_brick
                }
            )

            if save_response.status_code != 200:

                st.error(
                    save_response.text
                )
                st.stop()

            save_result = (
                save_response.json()
            )

            product_id = (
                save_result[
                    "product_id"
                ]
            )

            os.makedirs(
                "variant_uploads",
                exist_ok=True
            )

            saved_variant_paths = {}

            for (
                color,
                image_file
            ) in variant_images.items():

                filename = (
                    f"{product_id}_"
                    f"{color}_"
                    f"{image_file.name}"
                )

                filepath = os.path.join(
                    "variant_uploads",
                    filename
                )

                with open(
                    filepath,
                    "wb"
                ) as f:

                    f.write(
                        image_file.read()
                    )

                saved_variant_paths[
                    color
                ] = filepath

            for (
                color,
                image_path
            ) in saved_variant_paths.items():

                if selected_sizes:

                    for size in selected_sizes:

                        requests.post(
                            "http://127.0.0.1:8000/add-variant",
                            json={
                                "product_id":
                                    product_id,
                                "size":
                                    size,
                                "color":
                                    color,
                                "stock":
                                    stock,
                                "price":
                                    price,
                                "image_url":
                                    image_path
                            }
                        )

                else:

                    requests.post(
                        "http://127.0.0.1:8000/add-variant",
                        json={
                            "product_id":
                                product_id,
                            "size":
                                "N/A",
                            "color":
                                color,
                            "stock":
                                stock,
                            "price":
                                price,
                            "image_url":
                                image_path
                        }
                    )

            st.success(
                f"Product created successfully. "
                f"ID: {product_id}"
            )

            st.success(
                f"{len(saved_variant_paths)} "
                f"color variants created."
            )
