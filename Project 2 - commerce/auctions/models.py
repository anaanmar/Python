from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,related_name="user")
    description = models.TextField()
    price = models.IntegerField()
    category = models.CharField(max_length=64)
    link = models.CharField(max_length=256,default=None,blank=True,null=True)
    time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    listingid = models.ForeignKey(Listing, on_delete=models.CASCADE,related_name="bidlisting")
    userid = models.ForeignKey(User, on_delete=models.CASCADE,related_name="biduser")
    bid = models.IntegerField()
    closed = models.BooleanField(default=False)

class Comment (models.Model):
    listingid = models.ForeignKey(Listing, on_delete=models.CASCADE,related_name="commentlisting")
    userid = models.ForeignKey(User, on_delete=models.CASCADE,related_name="commentuser")
    comment = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

class Watchlist(models.Model):
   userid = models.ForeignKey(User, on_delete=models.CASCADE,related_name="watchlistuser")
   listingid = models.ForeignKey(Listing, on_delete=models.CASCADE,related_name="watchlistlisting")
   #listingid = models.ManyToManyField(Listing, blank= True, related_name="watchlistlisting")
