from django.contrib import admin
from .models import *
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',) }
    list_display = ['name', 'slug']

admin.site.register(Category, CategoryAdmin)

admin.site.register(Book)
admin.site.register(Review)
admin.site.register(BorrowBook)