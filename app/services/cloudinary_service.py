import cloudinary
import cloudinary.uploader

from dotenv import load_dotenv
import os

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


def upload_product_image(file_path):

    result = cloudinary.uploader.upload(
        file_path,
        folder="products"
    )

    return {
        "url": result["secure_url"],
        "public_id": result["public_id"]
    }