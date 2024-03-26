import re
import json

from django.http.request import QueryDict
from django.utils.datastructures import MultiValueDict

from .serializers import BlogSerializer
from .models import File, Blog, Magazine

from rest_framework.response import Response
from rest_framework import status


class BlogProcessor:
    """
    Utility class for processing blog data. The method "process_blog_data" 
        handles blog data processing, including validation and file handling.
    """

    @staticmethod
    def process_blog_data(request_method: str, blog_serializer: BlogSerializer, data: QueryDict, files: MultiValueDict) -> Response:
        """
        Processes blog data including validation and saving.

        Parameters:
            request_method (str): The HTTP request method ('POST' or 'PUT').
            blog_serializer (BlogSerializer): The serializer instance for the blog data.
            data (QueryDict): The data multipart data sent from the client for the blog.
            files (MultiValueDict): The files associated with the blog.

        Returns:
            Response: A response object indicating the status of the operation.
        """
        if request_method.upper() == 'POST':
            BLOG_FILES_SUCCESS = ApiResponse.BLOG_POST_FILES_SUCCESS
            BLOG_TEXT_SUCCESS = ApiResponse.BLOG_POST_TEXT_SUCCESS

        if request_method.upper() == 'PUT':
            BLOG_FILES_SUCCESS = ApiResponse.BLOG_PUT_FILES_SUCCESS
            BLOG_TEXT_SUCCESS = ApiResponse.BLOG_PUT_TEXT_SUCCESS

        if blog_serializer.is_valid():
            blog = blog_serializer.save()
            if len(files) != 0:
                BlogProcessor.__process_blog_files(blog, files, data.get('file_placeholders'))
                return Response(BLOG_FILES_SUCCESS, status=status.HTTP_201_CREATED)
            return Response(BLOG_TEXT_SUCCESS, status=status.HTTP_201_CREATED)
        return Response({"Error": blog_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def __process_blog_files(blog: Blog, files: dict, placeholders_json: str) -> None:
        """
        Processes files associated with the blog, and store 
            them at once in the DB through a bulk insert.

        Parameters:
            blog (Blog): A Blog instance.
            files (dict): Files to be processed and their name
            placeholders_json (str): A json list of objects with files,
                and their respective location in the text.
        """
        file_instances = []
        placeholders = json.loads(placeholders_json)
        for idx, key in enumerate(files):
            file_instance = {
                'blog': blog,
                'url': files[key],
                'uid': placeholders[idx][key]
            }
            file_instances.append(File(**file_instance))
        File.objects.bulk_create(file_instances)


class ApiResponse:
    """    
    Utility class providing predefined responses for API endpoints.
    """
    BLOG_POST_FILES_SUCCESS = {"Response": "Blog with files posted successfully."}
    BLOG_POST_TEXT_SUCCESS  = {"Response": "Blog with text only posted successfully."}
    READER_POST_SUCCESS     = {"Response": "Reader id added successfully."}
    BLOG_PUT_FILES_SUCCESS  = {"Response": "Blog with files updated successfully."}
    BLOG_PUT_TEXT_SUCCESS   = {"Response": "Blog with text only updated successfully."}
    BLOG_DELETE_SUCCESS     = {"Response": "Blog deleted successfully."}
    NOT_FOUND               = {"Response": "Item requested not found."}
    FILE_DELETE_SUCCESS     = {"Response": "File deleted successfully."}
    SERIALIZER_ERROR        = {"Error": "The error is most likely due to the data format."}
    FILE_DELETE_ERROR       = {"Error": "An error occured while trying to delete the file."}
    READER_POST_ERROR       = {"Erroe": "An error occured while trying to add the reader id."}

    @staticmethod
    def key_error(e: KeyError) -> dict:
        return {"Error": f"Missing key: {e}"}


def delete_file_placeholder(blog: str, uid: str) -> str:
    """
    Deletes the file placeholder of a deleted file in a blog.

    Parameters:
        blog (str): The text that includes placeholders denoting files.
        uid (str): The placeholder denoting files.

    Returns:
        str: The blog after deleting the placeholder.
    """
    pattern = str(uid)
    updated_blog = re.sub(pattern, f'', blog)
    return updated_blog


def latest_released_magazine_querydict() -> QueryDict:
    """
    Creates a query dictionary of the latest released 
        magazine id which can be used to make a subquery.

    Returns:
        QueryDict: A query dictionary to create a subquery.
    """
    magazine_subquery = Magazine.objects.filter(
        flag='released'
    ).order_by('-date_released').values('id')[:1]
    return magazine_subquery
