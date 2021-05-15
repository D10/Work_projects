from rest_framework import serializers

from .models import News


class NewsListSerializers(serializers.ModelSerializer):

    class Meta:
        model = News
        fields = ('pk', 'title', 'content')