from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, Group, Permission, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        blank=True,
        null=True,
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='backend_management_users_groups',
        related_query_name='user',
        help_text=_('The groups this user belongs to. A user will get all permissions '
                    'granted to each of their groups.'),
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='backend_management_users_permissions',
        related_query_name='user',
        help_text=_('Specific permissions for this user.'),
    )


class Project(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    file = models.FileField(upload_to='projects')
    approved = models.BooleanField(default=False)
    status_data = ((1, "APPROVED"), (2, "REJECTED"), (0, "PENDING"))
    status = models.CharField(default=0, choices=status_data, max_length=20)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects', null=True , limit_choices_to={'is_teacher': True})
    students = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_projects', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Idea(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ideas')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ideas')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
