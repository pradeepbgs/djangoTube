import cloudinary
import cloudinary.api
import cloudinary.uploader
from dotenv import load_dotenv
import os
from asgiref.sync import sync_to_async
import traceback

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True,
)

async def upload_image(image):
    try:
        return await sync_to_async(cloudinary.uploader.upload)(image)
    except Exception as e:
        print("Error during image upload:", traceback.format_exc())
        raise e  

async def upload_video_to_cloudinary(video):
    try:
        return await sync_to_async(cloudinary.uploader.upload)(video, resource_type="video")
    except Exception as e:
        print("Error during video upload:", traceback.format_exc())
        raise e 

async def delete_file_from_cloudinary(file_url, resource_type="image"):
    try:
        public_id = file_url.split("/").pop().split(".")[0]
        return await sync_to_async(cloudinary.uploader.destroy)(public_id, resource_type=resource_type)
    except Exception as e:
        print("Error during file deletion:", traceback.format_exc())
        raise e 
