from django.contrib import admin

# Register your models here.
from . models import User, Project, Idea, Comment, Message

# Register your models here.

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Idea)
admin.site.register(Comment)
admin.site.register(Message)