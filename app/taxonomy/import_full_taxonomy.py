import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

EXCEL_FILE = (
    "app/taxonomy/TAXONOMY_CATEGORIZATION_9TH.xlsx"
)

conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

cursor = conn.cursor()

xls = pd.ExcelFile(EXCEL_FILE)

print("SHEETS:")
print(xls.sheet_names)


import pandas as pd
import psycopg2




# ============================================================
# STEP 4 — SKIP JUNK SHEETS
# ============================================================

IGNORE_SHEETS = [
    "COLOR SCHEME",
    "Sheet1"
]


# ============================================================
# REQUIRED TAXONOMY COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "SegmentCode",
    "SegmentTitle",
    "FamilyCode",
    "FamilyTitle",
    "ClassCode",
    "ClassTitle",
    "BrickCode",
    "BrickTitle",
    "BrickDefinition_Includes",
    "AttributeCode",
    "AttributeTitle",
    "AttributeValueCode",
    "AttributeValueTitle",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_value(value):
    """
    Convert NaN/None to an empty string and
    remove unnecessary whitespace.
    """
    if pd.isna(value):
        return ""

    return str(value).strip()


def clean_code(value):
    """
    Convert Excel numeric codes such as:
        51000000.0
    into:
        51000000

    Blank values remain blank.
    """
    if pd.isna(value) or str(value).strip() == "":
        return None

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return str(value).strip()


def get_column(df, column_name):
    """
    Safely return a column.

    Some sheets may have slightly different columns.
    """
    if column_name in df.columns:
        return df[column_name]

    return pd.Series([""] * len(df), index=df.index)


# ============================================================
# CONNECT TO DATABASE
# ============================================================

try:

    # ========================================================
    # OPEN EXCEL FILE
    # ========================================================

    xls = pd.ExcelFile(EXCEL_FILE)

    print("========================================")
    print("STARTING TAXONOMY IMPORT")
    print("========================================")


    # ========================================================
    # STEP 5 — LOAD EVERY TAXONOMY SHEET
    # ========================================================

    for sheet in xls.sheet_names:

        # Skip junk sheets
        if sheet in IGNORE_SHEETS:
            print(f"\nSkipping sheet: {sheet}")
            continue

        print(f"\nProcessing sheet: {sheet}")

        # Read sheet
        df = pd.read_excel(
            EXCEL_FILE,
            sheet_name=sheet
        )

        # Replace NaN
        df = df.fillna("")


        # ----------------------------------------------------
        # CLEAN COLUMN NAME
        # ----------------------------------------------------

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]


        # ----------------------------------------------------
        # HANDLE TYPO IN CLEANING & HYGIENE
        # ----------------------------------------------------

        if "Attribute Code" in df.columns and "AttributeCode" not in df.columns:

            df = df.rename(
                columns={
                    "Attribute Code": "AttributeCode"
                }
            )


        # ----------------------------------------------------
        # CHECK THAT THIS IS A VALID TAXONOMY SHEET
        # ----------------------------------------------------

        if "SegmentCode" not in df.columns:

            print(
                f"Skipping {sheet} - "
                f"not a valid taxonomy sheet."
            )

            continue


        # ====================================================
        # STEP 6 — IMPORT SEGMENTS
        # ====================================================

        segment_columns = [
            "SegmentCode",
            "SegmentTitle"
        ]

        segments = df[segment_columns].copy()

        segments["SegmentCode"] = segments["SegmentCode"].apply(
            clean_code
        )

        segments["SegmentTitle"] = segments["SegmentTitle"].apply(
            clean_value
        )

        segments = segments[
            (segments["SegmentCode"].notna()) &
            (segments["SegmentTitle"] != "")
        ].drop_duplicates()


        for _, row in segments.iterrows():

            cursor.execute(
                """
                INSERT INTO segments
                (
                    segment_code,
                    segment_title
                )
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                (
                    row["SegmentCode"],
                    row["SegmentTitle"]
                )
            )


        print(
            f"  Segments processed: {len(segments)}"
        )


        # ====================================================
        # STEP 7 — IMPORT FAMILIES
        # ====================================================

        family_columns = [
            "FamilyCode",
            "FamilyTitle",
            "SegmentCode"
        ]

        families = df[family_columns].copy()

        families["FamilyCode"] = families["FamilyCode"].apply(
            clean_code
        )

        families["FamilyTitle"] = families["FamilyTitle"].apply(
            clean_value
        )

        families["SegmentCode"] = families["SegmentCode"].apply(
            clean_code
        )

        families = families[
            (families["FamilyCode"].notna()) &
            (families["FamilyTitle"] != "") &
            (families["SegmentCode"].notna())
        ].drop_duplicates()


        for _, row in families.iterrows():

            # Find parent segment
            cursor.execute(
                """
                SELECT id
                FROM segments
                WHERE segment_code = %s
                """,
                (
                    row["SegmentCode"],
                )
            )

            result = cursor.fetchone()

            if result is None:
                print(
                    f"  WARNING: Segment "
                    f"{row['SegmentCode']} not found."
                )
                continue

            segment_id = result[0]


            # Insert family
            cursor.execute(
                """
                INSERT INTO families
                (
                    family_code,
                    family_title,
                    segment_id
                )
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (
                    row["FamilyCode"],
                    row["FamilyTitle"],
                    segment_id
                )
            )


        print(
            f"  Families processed: {len(families)}"
        )


        # ====================================================
        # STEP 8 — IMPORT CLASSES
        # ====================================================

        class_columns = [
            "ClassCode",
            "ClassTitle",
            "FamilyCode"
        ]

        classes = df[class_columns].copy()

        classes["ClassCode"] = classes["ClassCode"].apply(
            clean_code
        )

        classes["ClassTitle"] = classes["ClassTitle"].apply(
            clean_value
        )

        classes["FamilyCode"] = classes["FamilyCode"].apply(
            clean_code
        )

        classes = classes[
            (classes["ClassCode"].notna()) &
            (classes["ClassTitle"] != "") &
            (classes["FamilyCode"].notna())
        ].drop_duplicates()


        for _, row in classes.iterrows():

            # Find parent family
            cursor.execute(
                """
                SELECT id
                FROM families
                WHERE family_code = %s
                """,
                (
                    row["FamilyCode"],
                )
            )

            result = cursor.fetchone()

            if result is None:
                print(
                    f"  WARNING: Family "
                    f"{row['FamilyCode']} not found."
                )
                continue

            family_id = result[0]


            # Insert class
            cursor.execute(
                """
                INSERT INTO classes
                (
                    class_code,
                    class_title,
                    family_id
                )
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (
                    row["ClassCode"],
                    row["ClassTitle"],
                    family_id
                )
            )


        print(
            f"  Classes processed: {len(classes)}"
        )


        # ====================================================
        # STEP 9 — IMPORT BRICKS
        # ====================================================

        brick_columns = [
            "BrickCode",
            "BrickTitle",
            "ClassCode",
            "BrickDefinition_Includes"
        ]

        # Only select columns that actually exist
        available_brick_columns = [
            col for col in brick_columns
            if col in df.columns
        ]

        bricks = df[available_brick_columns].copy()


        # Make missing column available
        if "BrickDefinition_Includes" not in bricks.columns:
            bricks["BrickDefinition_Includes"] = ""


        bricks["BrickCode"] = bricks["BrickCode"].apply(
            clean_code
        )

        bricks["BrickTitle"] = bricks["BrickTitle"].apply(
            clean_value
        )

        bricks["ClassCode"] = bricks["ClassCode"].apply(
            clean_code
        )

        bricks["BrickDefinition_Includes"] = (
            bricks["BrickDefinition_Includes"]
            .apply(clean_value)
        )


        bricks = bricks[
            (bricks["BrickCode"].notna()) &
            (bricks["BrickTitle"] != "") &
            (bricks["ClassCode"].notna())
        ].drop_duplicates()


        for _, row in bricks.iterrows():

            # Find parent class
            cursor.execute(
                """
                SELECT id
                FROM classes
                WHERE class_code = %s
                """,
                (
                    row["ClassCode"],
                )
            )

            result = cursor.fetchone()

            if result is None:
                print(
                    f"  WARNING: Class "
                    f"{row['ClassCode']} not found."
                )
                continue

            class_id = result[0]


            # Insert brick
            cursor.execute(
                """
                INSERT INTO bricks
                (
                    brick_code,
                    brick_title,
                    class_id,
                    includes_definition
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (
                    row["BrickCode"],
                    row["BrickTitle"],
                    class_id,
                    row["BrickDefinition_Includes"]
                )
            )


        print(
            f"  Bricks processed: {len(bricks)}"
        )


        # ============================================================
        # STEP 10 — IMPORT ATTRIBUTES
        # ============================================================

        attribute_columns = [
            "AttributeCode",
            "AttributeTitle",
            "BrickCode"
        ]

        attributes = df[attribute_columns].copy()

        attributes["AttributeCode"] = (
            attributes["AttributeCode"]
            .apply(clean_code)
        )

        attributes["AttributeTitle"] = (
            attributes["AttributeTitle"]
            .apply(clean_value)
        )

        attributes["BrickCode"] = (
            attributes["BrickCode"]
            .apply(clean_code)
        )

        # Only rows where attribute exists
        attributes = attributes[
            (attributes["AttributeCode"].notna()) &
            (attributes["AttributeTitle"] != "") &
            (attributes["BrickCode"].notna())
        ].drop_duplicates()


        for _, row in attributes.iterrows():

            # --------------------------------------------------------
            # Find parent brick
            # --------------------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM bricks
                WHERE brick_code = %s
                """,
                (
                    row["BrickCode"],
                )
            )

            result = cursor.fetchone()

            if result is None:

                print(
                    f"  WARNING: Brick "
                    f"{row['BrickCode']} not found."
                )

                continue

            brick_id = result[0]


            # --------------------------------------------------------
            # Find existing attribute for THIS brick
            # --------------------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM attributes
                WHERE attribute_code = %s
                AND brick_id = %s
                """,
                (
                    row["AttributeCode"],
                    brick_id
                )
            )

            result = cursor.fetchone()


            # --------------------------------------------------------
            # Insert attribute if it does not exist
            # --------------------------------------------------------

            if result is None:

                cursor.execute(
                    """
                    INSERT INTO attributes
                    (
                        attribute_code,
                        attribute_title,
                        brick_id
                    )
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (
                        row["AttributeCode"],
                        row["AttributeTitle"],
                        brick_id
                    )
                )

                attribute_id = cursor.fetchone()[0]

            else:

                attribute_id = result[0]


        print(
            f"  Attributes processed: {len(attributes)}"
        )


        # ============================================================
        # STEP 11 — IMPORT ATTRIBUTE VALUES
        # ============================================================

        attribute_value_columns = [
            "AttributeValueCode",
            "AttributeValueTitle",
            "AttributeCode",
            "BrickCode"
        ]

        attribute_values = df[
            attribute_value_columns
        ].copy()


        # ------------------------------------------------------------
        # AttributeValueType
        # ------------------------------------------------------------

        if "AttributeValueType" in df.columns:

            attribute_values["AttributeValueType"] = (
                df["AttributeValueType"]
                .apply(clean_value)
            )

        else:

            attribute_values["AttributeValueType"] = ""


        # ------------------------------------------------------------
        # Clean values
        # ------------------------------------------------------------

        attribute_values["AttributeValueCode"] = (
            attribute_values["AttributeValueCode"]
            .apply(
                lambda x:
                ""
                if pd.isna(x)
                else str(x).replace(".0", "").strip()
            )
        )

        attribute_values["AttributeValueTitle"] = (
            attribute_values["AttributeValueTitle"]
            .apply(clean_value)
        )

        attribute_values["AttributeCode"] = (
            attribute_values["AttributeCode"]
            .apply(clean_code)
        )

        attribute_values["BrickCode"] = (
            attribute_values["BrickCode"]
            .apply(clean_code)
        )


        # ------------------------------------------------------------
        # Only valid attribute values
        # ------------------------------------------------------------

        attribute_values = attribute_values[
            (attribute_values["AttributeValueCode"].notna()) &
            (attribute_values["AttributeValueCode"] != "") &
            (attribute_values["AttributeCode"].notna()) &
            (attribute_values["BrickCode"].notna())
        ].drop_duplicates()


        for _, row in attribute_values.iterrows():

            # --------------------------------------------------------
            # Find parent brick
            # --------------------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM bricks
                WHERE brick_code = %s
                """,
                (
                    row["BrickCode"],
                )
            )

            result = cursor.fetchone()

            if result is None:

                print(
                    f"  WARNING: Brick "
                    f"{row['BrickCode']} not found."
                )

                continue

            brick_id = result[0]


            # --------------------------------------------------------
            # Find attribute using BOTH:
            #
            # AttributeCode
            # Brick
            # --------------------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM attributes
                WHERE attribute_code = %s
                AND brick_id = %s
                """,
                (
                    row["AttributeCode"],
                    brick_id
                )
            )

            result = cursor.fetchone()


            if result is None:

                print(
                    f"  WARNING: Attribute "
                    f"{row['AttributeCode']} "
                    f"not found for brick "
                    f"{row['BrickCode']}."
                )

                continue


            attribute_id = result[0]


            # --------------------------------------------------------
            # Check whether this value already exists
            # for THIS attribute
            # --------------------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM attribute_values
                WHERE attribute_id = %s
                AND attribute_value_code = %s
                """,
                (
                    attribute_id,
                    row["AttributeValueCode"]
                )
            )

            existing_value = cursor.fetchone()


            # --------------------------------------------------------
            # Insert only if it does not exist
            # --------------------------------------------------------

            if existing_value is None:

                cursor.execute(
                    """
                    INSERT INTO attribute_values
                    (
                        attribute_value_code,
                        attribute_value_title,
                        attribute_id,
                        attribute_value_type
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        row["AttributeValueCode"],
                        row["AttributeValueTitle"],
                        attribute_id,
                        row["AttributeValueType"]
                    )
                )


        print(
            f"  Attribute values processed: "
            f"{len(attribute_values)}"
        )


    # ========================================================
    # STEP 12 — FINAL COMMIT
    # ========================================================

    conn.commit()

    print("\n========================================")
    print("IMPORT COMPLETE")
    print("========================================")


except Exception as e:

    # Rollback if anything goes wrong
    conn.rollback()

    print("\n========================================")
    print("IMPORT FAILED")
    print("========================================")

    print(f"Error: {e}")

    raise


finally:

    cursor.close()
    conn.close()

    print("\nDatabase connection closed.")