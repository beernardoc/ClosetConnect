from django.contrib import admin
from app.models import User, Product, Comment, Follower, Favorite
# Register your models here.

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Comment)
admin.site.register(Follower)
admin.site.register(Favorite)
