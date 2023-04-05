from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import ProjectListView, IdeaListView, UserLoginView


urlpatterns = [
    path('', views.index, name='home'),
    path('home/', views.index, name='home'),
    path('accounts/profile/', UserLoginView.as_view(), name='login'),
    path('send_message/<str:username>/', views.send_message, name='send_message'),
    #path('login/', views.login_view, name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    path("logout", views.logout_request, name= "logout"),
    path('register/', views.register, name='register'),
    path('search_project/', views.search_project, name='search_project'),
    path('create_project/', views.create_project, name='create_project'),
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent, name='sent'),
    path('send_message/<slug:username>/', views.send_message, name='send_message'),
    path('project_list/', ProjectListView.as_view(), name='project_list'),
    path('idea_list/', IdeaListView.as_view(), name='idea_list'),
    path('edit_project/<slug:short_name>/', views.edit_project, name='edit_project'),
    path('delete_project/<slug:short_name>/', views.delete_project, name='delete_project'),
    path('approve_project/<slug:short_name>/', views.approve_project, name='approve_project'),
    path('<slug:short_name>/', views.project_detail, name='project_detail'),
    path('suggest_idea/<slug:short_name>/', views.suggest_idea, name='suggest_idea'),
]
