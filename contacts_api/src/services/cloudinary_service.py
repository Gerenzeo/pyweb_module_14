import hashlib

import cloudinary
import cloudinary.uploader

from src.conf.config import settings

class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @staticmethod
    def genereate_name_avatar(email: str):
        """
        The genereate_name_avatar function takes an email address as a string and returns a unique avatar name.
        The function uses the hashlib module to generate a SHA256 hash of the email address, then truncates it to 10 characters.
        It then prepends &quot;avatars/&quot; to this string and returns it.
        
        :param email: str: Specify the type of parameter that is expected
        :return: A string with the name of an avatar
        """
        name = hashlib.sha256(email.encode("utf-8")).hexdigest()[:10]
        return f"avatars/{name}"

    @staticmethod
    def upload(file, public_id: str):
        """
        The upload function takes a file and public_id as arguments.
        The function then uploads the file to cloudinary using the public_id provided.
        If there is already an image with that id, it will be overwritten.
        
        :param file: Specify the file to be uploaded
        :param public_id: str: Set the public_id of the image to be uploaded
        :return: A dictionary of the uploaded file's information
        """
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return r

    @staticmethod
    def get_url_for_avatar(public_id, r):
        """
        The get_url_for_avatar function takes in a public_id and an r (which is the result of a cloudinary.uploader.explicit call)
        and returns the url for that avatar image, which will be used to display it on the page.
        
        :param public_id: Identify the image in cloudinary
        :param r: Get the version of the image from cloudinary
        :return: The url for the avatar image
        """
        src_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop="fill", version=r.get('version'))
        return src_url