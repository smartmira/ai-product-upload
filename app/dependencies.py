# app/dependencies.py

# -------------------------
# AI
# -------------------------

from app.ai.estimator import (
    estimate_dimensions
)

from app.ai.ai_weight_estimator import (
    estimate_weight_ai
)

from app.ai.size_color_suggester import (
    suggest_sizes_and_colors
)

from app.ai.attribute_extractor import (
    extract_attributes
)

from app.ai.gpt_classifier import (
    classify_product
)

from app.ai.detect_color import (
    detect_color
)

from app.ai.vision_surface_analyzer import (
    analyze_product_image
)

from app.ai.vision_feature_extractor import (
    extract_visual_features
)

# -------------------------
# TAXONOMY
# -------------------------

from app.taxonomy.taxonomy_matcher import (
    find_matches
)

from app.taxonomy.get_attribute_values import (
    get_attribute_values
)

# -------------------------
# DATABASE
# -------------------------

from app.db.save_product import (
    save_product
)

from app.db.save_variant import (
    save_variant
)

from app.db.save_variants import (
    save_variants
)

from app.db.get_product_variants import (
    get_product_variants
)

from app.db.get_product_images import (
    get_product_images
)

from app.db.get_sizes import (
    get_sizes
)

from app.db.get_colors import (
    get_colors
)

# -------------------------
# SERVICES
# -------------------------

from app.services.remove_background import (
    remove_background
)

# -------------------------
# EXPORTS
# -------------------------

__all__ = [

    # AI
    "estimate_dimensions",
    "estimate_weight_ai",
    "suggest_sizes_and_colors",
    "extract_attributes",
    "classify_product",
    "detect_color",
    "analyze_product_image",
    "extract_visual_features",

    # Taxonomy
    "find_matches",
    "get_attribute_values",

    # Database
    "save_product",
    "save_variant",
    "save_variants",
    "get_product_variants",
    "get_product_images",
    "get_sizes",
    "get_colors",

    # Services
    "remove_background",
]