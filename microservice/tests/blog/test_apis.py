import json
import uuid
import pytest
import factory

from rest_framework.test import APIClient
from django.utils import timezone

from blog.utils import ApiResponse
from blog.models import Blog, File

from tests.factories import (
    MagazineFactory, 
    FileFactory, 
    BlogFactory, 
    DraftFactory, 
    UserFactory, 
    FeedbackFactory,
    CategoryFactory, 
    DataGenerator, 
    release_magazines,
    fake
)

pytestmark = pytest.mark.django_db


class TestReadCurrentFeedApi:

    endpoint = '/api/magazine-feed/'

    def test_feed_get(self, api_client, file_factory: FileFactory) -> None:
        """
        Tests the retrieval of blogs on the feed through the API to ensure it is successful. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            file_factory (FileFactory): Used to create files associated to blogs in one go.
        """
        uuids = [str(uuid.uuid4()) for _ in range(2)] # creating unique uids to conform to the db design
        num_files = len(uuids)
        file_factory.create_batch(num_files, uid=factory.Iterator(uuids))
        release_magazines()
        response = api_client().get(self.endpoint)

        assert response.status_code == 200

    def test_feed_next_get(self, api_client, blog_factory: BlogFactory, magazine_factory: MagazineFactory) -> None:
        """
        Tests the retrieval of blogs on the feed's next page through the API to ensure it is successful. 
        
        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            magazine_factory (MagazineFactory): Used to create magazines.
        """
        magazine = magazine_factory()
        blog_factory.create_batch(20, magazine=magazine)
        release_magazines()
        response = api_client().get(self.endpoint)

        assert response.status_code == 200

        blogs = response.json()
        response = api_client().get(blogs['next'])

        assert response.status_code == 200


class TestReadArchivedFeedApi:

    endpoint = '/api/archived-magazine/'

    def test_feed_get(self, api_client, blog_factory: BlogFactory, magazine_factory: MagazineFactory) -> None:
        """
        Tests the retrieval of blogs of an old magazine through the API to ensure it is successful. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            magazine_factory (MagazineFactory): Used to create magazines.
        """
        client = api_client()
        magazine = magazine_factory()
        blog_factory.create_batch(2, magazine=magazine)
        release_magazines()

        data = {'magazine': magazine.pk}
        response = client.generic(
            method="GET", 
            path=self.endpoint, 
            data=json.dumps(data), 
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_feed_next_get(self, api_client, blog_factory: BlogFactory, magazine_factory: MagazineFactory) -> None:
        """
        Tests the retrieval of blogs on an old magazine feed's next page through the API to ensure it is successful. 
        
        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            magazine_factory (MagazineFactory): Used to create magazines.
        """
        client = api_client()
        magazine = magazine_factory()
        blog_factory.create_batch(20, magazine=magazine)
        release_magazines()

        data = {'magazine': magazine.pk}
        response = client.generic(
            method="GET", 
            path=self.endpoint, 
            data=json.dumps(data), 
            content_type='application/json'
        )

        assert response.status_code == 200

        blogs = response.json()
        response = api_client().generic(
            method="GET", 
            path=blogs['next'], 
            data=json.dumps(data), 
            content_type='application/json'
        )

        assert response.status_code == 200


class TestReadDraftsApi: 

    endpoint = '/api/read-drafts/'

    def test_drafts_get(self, api_client: APIClient, user_factory: UserFactory,  draft_factory: DraftFactory) -> None:
        """
        Tests the retrieval of the user's drafts through the API to ensure it is successful. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            user_factory (UserFactory): Used to create users.
            draft_factory (DraftFactory): Used to create drafts.
        """
        user = user_factory()
        client = api_client()
        draft_factory.create_batch(8, user=user)

        data = {'user' : user.id}
        response = client.generic(
            method="GET", 
            path=self.endpoint, 
            data=json.dumps(data), 
            content_type='application/json'
        )

        drafts = response.json()

        assert response.status_code == 200
        assert drafts['count'] == 8


class TestReadRejectedBlogsApi:

    endpoint = '/api/read-user-rejected-blogs/'

    def test_rejected_blogs_get(self, api_client: APIClient, blog_factory: BlogFactory, feedback_factory: FeedbackFactory) -> None: 
        """
        Tests the retrieval of the current user's rejected blogs and feedbacks through the API to ensure it is successful. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            feedback_factory (FeedbackFactory): Used to create feedbacks.
        """
        client = api_client()
        blog = blog_factory(is_approved=False, is_ready=False, is_rejected=True, rejection_number=1)
        feedback = feedback_factory(blog=blog, content=fake.sentence())

        data = {'user': blog.user_id}
        response = client.generic(
            method="GET", 
            path=self.endpoint, 
            data=json.dumps(data), 
            content_type='application/json'
        )

        rejected_blogs = response.json()

        assert response.status_code == 200
        assert rejected_blogs['results'][0]['feedbacks'][0]['content'] == feedback.content
        assert rejected_blogs['results'][0]['id'] == blog.pk


class TestReadBlogApi: 

    endpoint = '/api/read-blog/'

    def test_blog_get(self, api_client: APIClient, blog_factory: BlogFactory) -> None:
        """
        Tests the retrieval of a single blog through the API to ensure it is successful. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
        """
        client = api_client()
        blog = blog_factory()

        data = {'user': blog.user_id, 'blog': blog.id}
        response = client.generic(
            method="GET", 
            path=self.endpoint, 
            data=json.dumps(data), 
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_draft_get(self, api_client: APIClient, draft_factory: DraftFactory) -> None:
        """
        Tests the retrieval of a single draft through the API to ensure it is successful. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
        """
        client = api_client()
        draft = draft_factory()

        data = {'user': draft.user_id, 'blog': draft.id}
        response = client.generic(
            method="GET", 
            path=self.endpoint, 
            data=json.dumps(data), 
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_rejected_blog_get(self, api_client: APIClient, blog_factory: BlogFactory, feedback_factory: FeedbackFactory) -> None: 
        """
        Tests the retrieval of a rejected blog and its feedback through the API to ensure it is successful. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            feedback_factory (FeedbackFactory): Used to create feedbacks.
        """
        client = api_client()
        blog = blog_factory(is_approved=False, is_ready=False, is_rejected=True, rejection_number=1)
        feedback = feedback_factory(blog=blog, content=fake.sentence())

        data = {'user': blog.user_id, 'blog': blog.pk}
        response = client.generic(
            method="GET", 
            path=self.endpoint, 
            data=json.dumps(data), 
            content_type='application/json'
        )

        rejected_blog = response.json()
        
        assert response.status_code == 200
        assert rejected_blog['is_rejected'] == True
        assert rejected_blog['feedbacks'][0]['content'] == feedback.content

    def test_other_user_draft_get(self, api_client: APIClient, draft_factory: DraftFactory, user_factory: UserFactory) -> None:
        """
        Tests the retrieval of an other user's draft through the API to ensure it is forbidden. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            user_factory (UserFactory): Used to create users.
        """
        client = api_client()
        draft = draft_factory()
        user = user_factory()

        data = {'user': user.pk, 'blog' : draft.id}
        response = client.generic(
            method="GET", 
            path=self.endpoint, 
            data=json.dumps(data), 
            content_type='application/json'
        )

        assert response.status_code == 403

    def test_other_user_unapproved_blog_get(self, api_client: APIClient, blog_factory: BlogFactory, user_factory: UserFactory) -> None:
        """
        Tests the retrieval of an other user's unapproved blog through the API to ensure it is forbidden. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            user_factory (UserFactory): Used to create users.
        """
        client = api_client()
        blog = blog_factory(is_approved=False)
        user = user_factory()

        data = {'user': user.pk, 'blog' : blog.id}
        response = client.generic(
            method="GET", 
            path=self.endpoint, 
            data=json.dumps(data), 
            content_type='application/json'
        )

        assert response.status_code == 403


class TestReadUserBlogsApi: 

    endpoint = '/api/read-user-blogs/'

    def test_user_blogs_get(self, api_client: APIClient, user_factory: UserFactory,  blog_factory: BlogFactory) -> None:
        """
        Tests the retrieval of a user's blogs through the API to ensure it is successful. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            user_factory (UserFactory): Used to create users.
            blog_factory (BlogFactory): Used to create blogs.
        """
        user = user_factory()
        client = api_client()
        blog_factory.create_batch(5, user=user)
        
        data = {'author' : user.id}
        response = client.generic(
            method="GET", 
            path=self.endpoint, 
            data=json.dumps(data), 
            content_type='application/json'
        )

        blogs = response.json()

        assert response.status_code == 200
        assert blogs['count'] == 5


class TestCreateBlogApi: 

    endpoint = '/api/create-blog/'

    def test_blog_text_post(self, api_client: APIClient, blog_factory: BlogFactory, category_factory: CategoryFactory) -> None:
        """
        Tests the creation of blogs through the API with text only to ensure it is successful. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            category_factory (CategoryFacory): Used to create categories.
        """
        blog    = blog_factory()
        client  = api_client()
        names = ['Category 1', 'Category 2', 'Category 3']
        categories = category_factory.create_batch(3, name=factory.Iterator(names))

        data = DataGenerator.data_text(blog, *categories)
        response = client.post(self.endpoint, data=data, format='multipart')

        assert response.status_code == 201
        assert response.json() == ApiResponse.BLOG_POST_TEXT_SUCCESS

    def test_blog_files_post(self, api_client: APIClient, blog_factory: BlogFactory, category_factory: CategoryFactory) -> None:
        """
        Tests the creation of blogs through the API with text and files to ensure it is successful. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            category_factory (CategoryFacory): Used to create categories.
        """
        blog    = blog_factory()
        client  = api_client()
        names = ['Category 1', 'Category 2', 'Category 3']
        categories = category_factory.create_batch(3, name=factory.Iterator(names))

        data = DataGenerator.data_with_files(blog, *categories)
        response = client.post(self.endpoint, data=data, format='multipart')

        assert response.status_code == 201
        assert response.json() == ApiResponse.BLOG_POST_FILES_SUCCESS


class TestUpdateBlogApi:
    
    endpoint = '/api/update-blog/'

    def test_blog_text_put(self, api_client: APIClient, blog_factory: BlogFactory, category_factory: CategoryFactory) -> None:
        """
        Tests the update of blogs with text through the API to ensure it is successful. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            category_factory (CategoryFacory): Used to create categories.
        """
        client = api_client()
        names = ['Category 1', 'Category 2', 'Category 3']
        categories = category_factory.create_batch(3, name=factory.Iterator(names))
        blog_initial_data = blog_factory(
            title=fake.sentence(), 
            content=fake.paragraph(), 
            date_created=self.__generate_random_datetime()
        )
        blog_updated_data = blog_factory(
            title=fake.sentence(), 
            content=fake.paragraph(),
            date_created=timezone.now()
        )
        blog = self.__initial_blog(blog_initial_data)
        data = {
            'blog': blog.pk,
            'user': blog.user.pk,
            'category_ids': json.dumps([category.pk for category in categories]),
            'title': blog_updated_data.title,
            'content': blog_updated_data.content,
            'is_draft': False,
        }
        response = client.put(self.endpoint, data=data, format='multipart')

        blog = Blog.objects.get(pk=blog.pk)

        assert response.status_code           == 201
        assert response.json()                == ApiResponse.BLOG_PUT_TEXT_SUCCESS
        assert blog_updated_data.title        == blog.title
        assert blog_updated_data.content      == blog.content
        assert 'date_updated was handled by the server (Not None)', blog.date_updated

    def test_blog_files_put(self, api_client: APIClient, blog_factory: BlogFactory, category_factory: CategoryFactory) -> None:
        """
        Tests the update of blogs with files through the API to ensure it is successful. 

        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            category_factory (CategoryFacory): Used to create categories.
        """
        client = api_client()
        names = [fake.name(), fake.name(), fake.name()]
        categories = category_factory.create_batch(3, name=factory.Iterator(names))
        blog_initial_data = blog_factory(
            title=fake.sentence(), 
            content=fake.paragraph(), 
            date_created=self.__generate_random_datetime()
        )
        blog_updated_data = blog_factory(
            title=fake.sentence(), 
            content=fake.paragraph(),
            date_created=timezone.now()
        )
        blog = self.__initial_blog(blog_initial_data)
        data = DataGenerator.data_with_files(blog_updated_data, *categories)
        # non-amendable fields
        data['blog'] = blog.pk
        data['user'] = blog.user.pk
        # keep data content to make sure it has been updated by the server
        updated_content  = data['content']
        response = client.put(self.endpoint, data=data, format='multipart')

        blog = Blog.objects.get(pk=blog.pk)

        assert response.status_code     == 201
        assert response.json()          == ApiResponse.BLOG_PUT_FILES_SUCCESS
        assert blog_updated_data.title  == blog.title
        assert updated_content          == blog.content
        assert 'date_updated was handled by the server (Not None)', blog.date_updated

    def __initial_blog(self, blog_initial_data: BlogFactory) -> Blog:
        """
        Helper method to create new blogs and store them the database.

        Parameters:
            blog_initial_data (BlogFactory): The source of the data.
        Returns:
            Blog: A Blog instance.
        """
        blog = Blog.objects.create(
            title        = blog_initial_data.title,
            content      = blog_initial_data.content,
            is_approved  = blog_initial_data.is_approved,
            is_draft     = blog_initial_data.is_draft,
            date_created = blog_initial_data.date_created,
            keywords     = blog_initial_data.keywords,
            user         = blog_initial_data.user,
            magazine     = blog_initial_data.magazine,
        )
        return blog
    
    def __generate_random_datetime(self) -> str:
        """
        Helper function to generate random time formatted suitably for the database.
        """
        random_date_time = fake.date_time_this_month()
        formatted_date_time = random_date_time.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_date_time


class TestDeleteBlogApi: 

    endpoint = '/api/delete-blog/'

    def test_blog_delete(self, api_client: APIClient, blog_factory: FileFactory) -> None:
        """
        Tests the deletion of blogs through the API to ensure it is successful. 
        
        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
        """
        blog    = blog_factory()
        client  = api_client()

        assert Blog.objects.filter(pk=blog.id).exists()

        data = {'user': blog.user.pk, 'blog': blog.id}
        client.delete(self.endpoint, data=data, format='json')

        assert not Blog.objects.filter(pk=blog.id).exists()

    def test_other_user_blog_delete(self, api_client: APIClient, blog_factory: FileFactory, user_factory: UserFactory) -> None:
        """
        Tests the deletion of another user's blog through the API to ensure it is forbidden. 
        
        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            user_factory (UserFactory): Used to create users.
        """
        blog    = blog_factory()
        user    = user_factory()
        client  = api_client()

        data = {'user': user.pk, 'blog': blog.id}
        response = client.delete(self.endpoint, data=data, format='json')

        assert response.status_code == 403


class TestDeleteFileApi: 

    endpoint = '/api/delete-file/'

    def test_delete_file(self, api_client: APIClient, file_factory: FileFactory) -> None:
        """
        Tests the deletion of files and their placeholder in the
            blog's text through the API to ensure it is successful. 
        
        Parameters:
            api_client (APIClient): The library used to make requests.
            file_factory (FileFactory): Used to create files associated to blogs in one go.
        """
        file         = file_factory()
        client       = api_client()
        file_id      = file.id
        file_uid     = str(file.uid)
        blog         = file.blog
        blog_id      = blog.id
        blog_content = blog.content
        
        assert file_uid in blog_content

        data = {'user': file.blog.user.pk, 'file': file_id}
        client.delete(self.endpoint, data=data, format='json')

        updated_blog = Blog.objects.get(pk=blog_id)
        updated_content = updated_blog.content

        assert file_uid not in updated_content
        assert not File.objects.filter(pk=file_id).exists()

    def test_delete_other_user_file(self, api_client: APIClient, file_factory: FileFactory, user_factory: UserFactory) -> None:
        """
        Tests the deletion of an other user's file through the API to ensure it is forbidden. 
        
        Parameters:
            api_client (APIClient): The library used to make requests.
            file_factory (FileFactory): Used to create files associated to blogs in one go.
            user_factory (UserFactory): Used to create users.
        """
        file   = file_factory()
        user   = user_factory()
        client = api_client()
        
        data = {'user': user.pk, 'file': file.id}
        response = client.delete(self.endpoint, data=data, format='json')

        assert response.status_code == 403


class TestAddReaderApi: 

    endpoint = '/api/add-reader/'

    def test_reader_post(self, api_client: APIClient, blog_factory: BlogFactory, user_factory: UserFactory) -> None:
        """
        Tests the addition of a new reader to the list of a blog readers through the API to ensure it is successful. 
        
        Parameters:
            api_client (APIClient): The library used to make requests.
            blog_factory (BlogFactory): Used to create blogs.
            user_factory (UserFactory): Used to create users.
        """
        blog    = blog_factory()
        user    = user_factory()
        client  = api_client()
        blog_id = blog.pk

        data = {'user': user.pk, 'blog': blog_id}
        response = client.post(self.endpoint, data=data, format='json')

        blog = Blog.objects.get(pk=blog_id)

        assert response.status_code == 201
        assert response.json() == ApiResponse.READER_POST_SUCCESS
        assert str(user.pk) in blog.reader_ids