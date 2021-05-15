from django.db import models


class News(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата новости')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата редактирования новости')
    title = models.CharField(max_length=150, verbose_name='Заголовок новости')
    content = models.TextField(verbose_name='Текст новости')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
