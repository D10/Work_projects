from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from .models import News
from .serializers import NewsListSerializers


class NewsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        news = News.objects.all()
        serializers = NewsListSerializers(news, many=True)
        return Response(serializers.data)
