from rest_framework import serializers

from shop.models import Book, UserBookRelation


class BookSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'author_name', 'price', 'likes_count', 'average_rating')


class UserBookRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmarks', 'rate')
