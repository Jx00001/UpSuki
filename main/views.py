from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, FileResponse
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from .models import FilePost, UserData
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from string import ascii_lowercase, ascii_uppercase, digits
from random import sample
from hashlib import sha256

code_generator = lambda: "".join(sample(ascii_lowercase+ascii_uppercase+digits, 8))

def get_hash(file):
    hash_object = sha256()
    for chunk in iter(lambda: file.read(4096), b""):
        hash_object.update(chunk)
    return hash_object.hexdigest()

def home(request):
    if request.method == 'POST':
        if 'hash' in request.POST:
            hash = request.POST.get('hash')
            files = FilePost.objects.filter(file_hash=hash)
            if len(files) != 0:
                file = files[0]
                return HttpResponseRedirect(f"/download/{file.file_code}")
            messages.error(request, "There is no File in Our DataBase related to that hash." )
            return redirect('home')
        else:
            file = request.FILES['file']
            file_code = code_generator()

            if request.user.is_authenticated:
                upload_file = FilePost(user=request.user, file=file, file_hash=get_hash(file.open()), name=file.name, file_code=file_code)
                upload_file.save()
            else:
                upload_file = FilePost(user=User.objects.get(username="guest"), file=file, file_hash=get_hash(file.open()), name=file.name, file_code=file_code)
                upload_file.save()
            return JsonResponse({'redirect_url' : f'/download/{file_code}'})    
    else:
        if request.user.is_authenticated: session = request.user.username
        else: session = "Guest"
        return render(request, "index.html", {'session' : session})


def download(request, file_code):
    if request.method == 'POST':
        return FileResponse(FilePost.objects.get(file_code=file_code).file, as_attachment=True)
    else:
        try:
            file = FilePost.objects.get(file_code=file_code)
        except ObjectDoesNotExist:
            messages.error(request, "Invalid File Code URL." )
            return redirect('home')
        if request.user.is_authenticated: name = request.user.username
        else: name = "Guest"
        return render(request, 'download.html', {'file' : file, 'session' : name})

def library(request):
    if request.user.is_authenticated:
        name = request.user.username
        if request.method == 'POST':
            if 'delete' in request.POST:
                file_code = request.POST.get('delete')
                file = FilePost.objects.get(file_code=file_code)
                file.delete()
            return redirect('library')
        else:
            files = FilePost.objects.filter(user=request.user)
            return render(request, 'library.html', {'files': files, 'session': name})

def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            uname = request.POST['username']
            pwd = request.POST['pwd']
            check_user = authenticate(username = uname, password = pwd)
            if check_user is not None:
                login(request, check_user)
                return redirect('home')
            else:
                check_user = authenticate(username = uname.lower(), password = pwd)
                if check_user is not None:
                    login(request, check_user)
                    return redirect('home') 
                else:                  
                    messages.warning(request, 'Invalid Username or Password.')
                    return redirect('user_login')
        else:
            return render(request, "login.html")

    else:
        return redirect('home')

def user_signup(request):
    if request.method == 'POST':
        first_name = request.POST['username']
        mail = request.POST['email']
        pwd = request.POST['pwd']
        new_user = User.objects.create_user(first_name, mail, pwd)
        new_user.first_name = first_name
        new_user.save()
        check_user = authenticate(username = first_name, password = pwd)
        if check_user is not None:
            login(request, check_user)
            return redirect('home')
        else:
            return redirect('home')
    else:
        return render(request, "signup.html")

def user_logout(request):
    logout(request)
    return redirect('home')
