from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from .validators import validate_no_special_characters
from django.core.validators import MinValueValidator


# Create your models here.
class User(AbstractUser):
    nickname = models.CharField(
        max_length=15, 
        unique=True, 
        null=True,
        validators=[validate_no_special_characters],
        # error_message={"unique": ""}
    )
    whatsapp_id = models.CharField(
        max_length=20, 
        null=True,
        validators=[validate_no_special_characters],
        )
    address = models.CharField(
        max_length=50, 
        null=True,
        validators=[validate_no_special_characters],
        )
    
    profile_pic = models.ImageField(default='default_profile_pic.jpg', upload_to='profile_pics')
    
    def __str__(self):
        return self.email
    
    following = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='followers')




class Post(models.Model):
    title = models.CharField(max_length=60)

    item_price = models.IntegerField(validators=[MinValueValidator(1)])

    CONDITION_CHOICES = [
        ('New', 'New'),
        ('Very Good', 'Very Good'),
        ('Good', 'Good'),
        ('Fine', 'Fine'),
        ('Bad', 'Bad'),
    ]
    item_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default=None)

    item_details = models.TextField(blank=True)

    image1 = models.ImageField(upload_to='item_pics')

    image2 = models.ImageField(upload_to='item_pics', blank=True)

    image3 = models.ImageField(upload_to='item_pics', blank=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    likes = GenericRelation('Like', related_query_name='post')

    dt_created = models.DateTimeField(auto_now_add=True)

    dt_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    is_sold = models.BooleanField(default=False)

    class Meta:
        ordering = ['-dt_created']




class Comment(models.Model):
    content = models.TextField(max_length=500, blank=False)

    dt_created = models.DateTimeField(auto_now_add=True)

    dt_updated = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    likes = GenericRelation('Like', related_query_name='comment')

    def __str__(self):
        return self.content[:30]
    
    class Meta:
        ordering = ['dt_created']




class Like(models.Model):
    dt_created = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    object_id = models.PositiveIntegerField()

    liked_object = GenericForeignKey()

    def __str__(self):
        return f"({self.user}, {self.liked_object})"




