from django.contrib import admin

# Register your models here.
from skillblog.models import Posts, Resume

admin.site.register(Posts)
admin.site.register(Resume)

