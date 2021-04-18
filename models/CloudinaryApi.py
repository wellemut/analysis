import os
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
)

# Create an authenticated Cloudinary client
class CloudinaryApi:
    @staticmethod
    def upload(image):
        response = cloudinary.uploader.upload(
            file=image,
            folder="global-goals-directory",
            overwrite=False,
        )

        return response["secure_url"]
