from django.contrib import admin

from news.models import News


class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'title', 'content')


admin.site.register(News, NewsAdmin)
