from django.contrib import admin

from shop.models import Book, UserBookRelation

admin.site.register(Book)
admin.site.register(UserBookRelation)