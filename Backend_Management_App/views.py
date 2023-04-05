from django.contrib.auth import login, logout, authenticate
from .models import User
from django.contrib.auth.views import LoginView
from .forms import UserRegistrationForm
from django.shortcuts import render, redirect
from django.contrib.auth import logout
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from Backend_Management_App.models import Project, Idea, Message, Comment, User
from Backend_Management_App.forms import ProjectForm, IdeaForm, MessageForm, CommentForm
from django.core.files.storage import FileSystemStorage
from django.views.generic import ListView

from Backend_Management_App.custom_authenticate import UserTypeBackend
from .models import Project


def index(request):
    projects = Project.objects.all()
    context = {'projects': projects}
    return render(request, 'index.html', context)


class ProjectListView(ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        print("Uploaded file URL:", uploaded_file_url)
        if form.is_valid():
            project = form.save(commit=False)
            project.students = request.user
            project.file = uploaded_file_url
            project.save()
            messages.success(request, 'Your project has been created.')
            return redirect('project_detail', short_name=project.short_name)
    else:
        form = ProjectForm()
    context = {'form': form}
    return render(request, 'create_project.html', context)


@login_required(login_url='login')
def edit_project(request, short_name):
    pj = Project.objects.get(short_name=short_name)
    if request.user.user_type == 'admin':
        project = get_object_or_404(Project, short_name=short_name)
    elif request.user == pj.teacher:
        project = get_object_or_404(
            Project, short_name=short_name, teacher=request.user)
    elif request.user == pj.students:
        project = get_object_or_404(
            Project, short_name=short_name, students=request.user)
    else:
        messages.error(request, "You are not authorized to edit this project.")
        
        return redirect('project_list')
        
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your project has been updated.')
            return redirect('project_detail', short_name=project.short_name)
    else:
        form = ProjectForm(instance=project)
    context = {'form': form, 'project': project}
    return render(request, 'edit_project.html', context)


@login_required(login_url='login')
def delete_project(request, short_name):
    # project = get_object_or_404(Project, short_name=short_name, teacher=request.user)
    pj = Project.objects.get(short_name=short_name)
    if request.user.user_type == 'admin':
        project = get_object_or_404(Project, short_name=short_name)
    elif request.user == pj.teacher:
        project = get_object_or_404(
            Project, short_name=short_name, teacher=request.user)
    elif request.user == pj.students:
        project = get_object_or_404(
            Project, short_name=short_name, students=request.user)
    else:
        messages.error(request, "You are not authorized to delete this project.")
        return redirect('project_list')
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Your project has been deleted.')
        return redirect('home')
    context = {'project': project}
    return render(request, 'delete_project.html', context)


@login_required
def approve_project(request, short_name):
    project = get_object_or_404(Project, short_name=short_name)
    """if project.students.count() == 0:
        raise PermissionDenied('This project has no students.')"""
    print(project.id)
    project.approved = True
    project.status = 1
    project.teacher = request.user
    project.save()
    messages.success(request, 'The project has been approved.')
    return redirect('project_detail', short_name=short_name)


@login_required(login_url='login')
def project_detail(request, short_name):
    project = get_object_or_404(Project, short_name=short_name)
    """if not project.approved and project.teacher != request.user and project.students.filter(id=request.user.id).count() == 0:
        raise PermissionDenied('This project has not been approved yet.')"""
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been posted.')
            return redirect('project_detail', short_name=project.short_name)
    else:
        form = CommentForm()
    comments = Comment.objects.filter(project=project)
    context = {'project': project, 'form': form, 'comments': comments}
    return render(request, 'project_detail.html', context)


@login_required(login_url='login')
def search_project(request):
    query = request.GET.get('q')
    if query:
        projects = Project.objects.filter(title__icontains=query)
    else:
        projects = Project.objects.all()
    context = {'projects': projects, 'query': query}
    return render(request, 'search_project.html', context)


@login_required
def download_project(request, short_name):
    project = get_object_or_404(Project, short_name=short_name)
    if not project.approved and project.teacher != request.user and project.students.filter(id=request.user.id).count() == 0:
        raise PermissionDenied('This project has not been approved yet.')
    file_path = project.file.path
    with open(file_path, 'rb') as fh:
        response = HttpResponse(
            fh.read(), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=' + \
            os.path.basename(file_path)
        return response
    raise Http404


"""
@login_required
def register_project(request, short_name):
    project = get_object_or_404(Project, short_name=short_name)
    if project.students.filter(id=request.user.id).count() == 1:
        messages.warning(request, 'You have already registered for this project.')
        return redirect('project_detail', short_name=project.short_name)
    if request.method == 'POST':
        project.students.add(request.user)
        messages.success(request, 'You have successfully registered for this project.')
        return redirect('project_detail', short_name=project.short_name)
    context = {'project': project}
    return render(request, 'register_project.html', context)
"""


class IdeaListView(ListView):
    model = Idea
    template_name = 'idea_list.html'
    context_object_name = 'ideas'


@login_required
def suggest_idea(request, short_name):
    project = get_object_or_404(Project, short_name=short_name)
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.project = project
            idea.teacher = request.user
            idea.save()
            messages.success(request, 'Your idea has been submitted.')
            return redirect('project_detail', short_name=project.short_name)
    else:
        form = IdeaForm()
    context = {'form': form, 'project': project}
    return render(request, 'suggest_idea.html', context)


@login_required
def send_message(request, username):
    # recipient = get_object_or_404(User, username=username)
    if request.method == 'POST':
        # form = MessageForm(request.POST)
        recipient = request.POST['recipient']
        subject = request.POST['subject']
        body = request.POST['body']

        receiver = get_object_or_404(User, id=recipient)
        message = Message(receiver=receiver, subject=subject,
                          body=body, sender=request.user)
        message.save()
        messages.success(request, 'Your message has been sent.')
        return redirect('sent')
    else:
        form = MessageForm()
    context = {'form': form, 'users': User.objects.all}
    return render(request, 'send_message.html', context)


@login_required
def inbox(request):
    cnt = Message.objects.filter(receiver=request.user).count()
    messages = Message.objects.filter(receiver=request.user)
    context = {'messages': messages, 'cnt': cnt}
    return render(request, 'inbox.html', context)


@login_required
def sent(request):
    messages = Message.objects.filter(sender=request.user)
    context = {'messages': messages}
    return render(request, 'sent.html', context)


def logout_request(request):
    logout(request)
    return redirect("home")


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_student = form.cleaned_data['user_type'] == 'student'
            user.is_teacher = form.cleaned_data['user_type'] == 'teacher'
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            # login(request, user)
            return redirect('login')
    else:
        form = UserRegistrationForm()
    context = {'form': form}
    return render(request, 'register.html', context)


"""from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        print(user)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error_message = "Invalid username or password."
            return render(request, 'login.html', {'error_message': error_message})
    
    return render(request, 'login.html')
"""


# use default LoginView for login


class UserLoginView(LoginView):
    model = User
    template_name = 'login.html'
    authentication_backend = 'Backend_Management_App.custom_authenticate.UserTypeBackend'
    success_url = reverse_lazy('home')


"""def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('project_list')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    context = {'form': form}
    return render(request, 'login.html', context)

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')
"""
