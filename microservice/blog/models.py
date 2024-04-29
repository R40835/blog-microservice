from django.db import models
from django.contrib.postgres.fields import ArrayField


class Role(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'role'


class User(models.Model):
    first_name          = models.CharField(max_length=255, null=False, blank=False)
    last_name           = models.CharField(max_length=255, null=False, blank=False)
    email               = models.EmailField(max_length=255, unique=True, null=False, blank=False)
    profile_photo       = models.ImageField(upload_to="images/", null=False, blank=False)
    date_of_birth       = models.DateField(null=True, blank=True)
    date_created        = models.DateField(null=True, blank=True)
    date_updated        = models.DateField(null=True, blank=True)
    last_login_date     = models.DateField(null=True, blank=True)
    email_notification  = models.BooleanField(null=True, blank=True)
    nationality         = models.CharField(max_length=255, null=True, blank=True)
    type                = models.CharField(max_length=255, null=True, blank=True)
    gender              = models.CharField(max_length=255, null=True, blank=True)
    banned              = models.BooleanField(default=False, null=True, blank=True)

    role                = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user'


class Magazine(models.Model): 
    title         = models.CharField(max_length=255)
    flag          = models.CharField(max_length=255) 
    date_created  = models.DateTimeField()
    date_released = models.DateTimeField()

    class Meta:
        db_table = 'magazine'


class ScheduledJobs(models.Model):
    job_id          = models.CharField(primary_key=True)
    magazine        = models.ForeignKey(Magazine, on_delete=models.CASCADE)
    magazine_title  = models.CharField(max_length=255)
    status          = models.CharField(max_length=255)
    updated_time    = models.DateTimeField()
    release_date    = models.DateTimeField()

    class Meta:
        db_table = 'scheduled_jobs'


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'category'


class Blog(models.Model): 
    title               = models.CharField(max_length=255)
    content             = models.TextField(max_length=5000) 
    is_approved         = models.BooleanField(default=False)
    is_draft            = models.BooleanField(default=False)
    is_rejected         = models.BooleanField(default=False) 
    is_ready            = models.BooleanField(default=True)
    rejection_number    = models.IntegerField(default=0) 
    date_created        = models.DateTimeField(null=False, blank=False)
    date_updated        = models.DateTimeField(null=True, blank=True)
    reader_ids          = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    keywords            = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    likes               = models.PositiveIntegerField(default=0, null=False, blank=False) 
    comments            = models.PositiveIntegerField(default=0, null=False, blank=False) 
    readers             = models.PositiveIntegerField(default=0, null=False, blank=False) 

    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    magazine            = models.ForeignKey(Magazine, on_delete=models.CASCADE)
    categories          = models.ManyToManyField(Category, related_name='blogs')

    class Meta:
        db_table = 'blog'
        ordering = ['-date_created']
        managed = True


class File(models.Model):
    uid  = models.UUIDField(unique=True)
    url  = models.FileField(upload_to='files/')

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='files') 

    class Meta:
        db_table = 'file'


class Like(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE)
    blog      = models.ForeignKey(Blog, on_delete=models.CASCADE)

    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'like'


class Comment(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE)
    blog      = models.ForeignKey(Blog, on_delete=models.CASCADE)
    text      = models.TextField(max_length=500)

    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'comment'


class Feedback(models.Model):
    blog    = models.ForeignKey(Blog, related_name='feedbacks', on_delete=models.CASCADE)
    content = models.TextField(max_length=500)

    class Meta:
        db_table = 'feedback'


class EmailNotification(models.Model):
    email   = models.EmailField(primary_key=True)
    id      = models.BigIntegerField(unique=True)
    type    = models.CharField(max_length=255)
    text    = models.TextField(max_length=500)
    success = models.BooleanField()

    class Meta:
        db_table = 'email_notification'


class AppNotification(models.Model):
    type      = models.CharField(max_length=255)
    text      = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    blog      = models.ForeignKey(Blog, on_delete=models.CASCADE)
    sender    = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    receiver  = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)

    class Meta:
        db_table = 'app_notification'
        ordering = ['-timestamp']
