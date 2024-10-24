from django.contrib import admin
from .models import Category, Media, Comment, View, Like,OriginalLanguage
# Register your models here.
admin.site.register(Category)
admin.site.register(Media)
admin.site.register(Comment)
admin.site.register(View)
admin.site.register(Like)
admin.site.register(OriginalLanguage)