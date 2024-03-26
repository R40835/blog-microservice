import pytest

from tests.factories import BlogFactory, FileFactory
from blog.models import Blog, File

# Grant access to the DB
pytestmark = pytest.mark.django_db


class TestBlogModel: 
    def test_create(self, blog_factory: BlogFactory) -> None:
        """
        Tests the creation of blogs to ensure it is successful, 
            and verifies that all attributes match the factory values.

        Parameters:
            blog_factory (BlogFactory): A factory object to create blog instances.
        """
        blog = blog_factory()

        assert blog.title           == BlogFactory.title
        assert blog.content         == BlogFactory.content
        assert blog.is_approved     == BlogFactory.is_approved
        assert blog.is_draft        == BlogFactory.is_draft
        assert blog.date_created    == BlogFactory.date_created
        assert blog.reader_ids      == BlogFactory.reader_ids
        assert blog.keywords        == BlogFactory.keywords

    def test_update(self, blog_factory: BlogFactory) -> None:
        """
        Tests the update of blogs to ensure it is successful, 
            and verifies that all attributes match the new values.

        Parameters:
            blog_factory (BlogFactory): A factory object to create a blog instance.
        """
        blog = blog_factory()

        new_title       = "Updated Title"
        new_content     = "Updated Content"
        new_keywords    = ["updated keyword"]
        new_reader_id   = "16"
        blog.title      = new_title
        blog.content    = new_content
        blog.keywords   = new_keywords
        blog.reader_ids.append(new_reader_id)

        blog.save()

        updated_blog = Blog.objects.get(id=blog.id)
        
        assert updated_blog.title    == new_title
        assert updated_blog.content  == new_content
        assert updated_blog.keywords == new_keywords
        assert "16" in updated_blog.reader_ids


class TestFileModel:
    def test_create(self, file_factory: FileFactory) -> None:
        """
        Tests the creation of files to ensure it is successful, 
            and verifies that files (images/videos) are uploaded gracefully.

        Parameters:
            blog_factory (BlogFactory): A factory object to create a blog instance.
        """
        file = file_factory()

        assert file.url, "File uploaded"
        assert file.uid == FileFactory.uid

    def test_delete_cascading(self, file_factory: FileFactory) -> None:
        """
        Tests deletion of a Blog instance and verify 
            cascading deletion of associated File instances.

        Parameters:
            file_factory (FileFactory): A factory object to create a file instance.
        """
        file = file_factory()

        blog_id = file.blog_id
        file_id = file.pk
        blog    = Blog.objects.get(pk=blog_id)

        blog.delete()

        assert not File.objects.filter(pk=file_id).exists()

