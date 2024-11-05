import cloudinary
import cloudinary.api
import cloudinary.uploader
from dotenv import load_dotenv
import os
from asgiref.sync import sync_to_async

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True,
)

async def upload_image(image):
    upload_result = await sync_to_async(cloudinary.uploader.upload)(image)
    return upload_result

async def upload_video(video):
    upload_result = await sync_to_async(cloudinary.uploader.upload)(video,resource_type="video")
    return upload_result

async def delete_post(image_url):
    public_id = image_url.split("/").pop().split(".")[0]
    return await sync_to_async(cloudinary.uploader.destroy(public_id))()