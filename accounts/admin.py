from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Library)
admin.site.register(UserLibraryAccount)
admin.site.register(UserAddress)
admin.site.register(Transaction)
admin.site.register(Comment)