from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room,Topic,Message
from .forms import RoomForm
# Create your views here.
from django.http import HttpResponse

rooms = [
    {'id':'1','name':'Django learners'},
    {'id':'2','name':'Frontend developers'},
    {'id':'3','name':'Designers'}
]




def loginpage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username) 
        except:
            messages.error(request, "User doesnot exist.")
        
        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"Username or Password does not exist.")

    context = {'page':page}
    return render(request,'base/login_register.html',context)


def logoutuser(request):
    logout(request)
    return redirect('home')


def registerpage(request):
    page='register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"An error occured during registration.")
    context = {'page':page,'form':form}
    return render(request,'base/login_register.html',context) 


def home(request):
    q = request.GET.get('q')
    if q==None:
        q=''
    # print(q)
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    topics = Topic.objects.all()
    context = {
        'rooms':rooms,
        'topics':topics,
        'room_count':room_count,
        'room_messages':room_messages,
    }
    return render(request,'base/home.html',context)



def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    # print(room_messages)
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body'),
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    print(participants)
    context = {'room':room,'room_messages':room_messages,'participants':participants}
    return render(request,'base/room.html',context)


def userprofile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context ={'user':user,'rooms':rooms,'topics':topics,'room_messages':room_messages}
    return render(request,'base/profile.html',context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    # print(form)
    # print(request,method)
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'form':form} 
    return render(request,'base/room_form.html',context)



@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    print(request)
    if request.user != room.host:
        return HttpResponse("You are not allowed to edit this room.")

    if request.method == 'POST':
        form = RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request,'base/room_form.html',context)



@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    # print(request.method)
    if request.user != room.host:
        return HttpResponse("You are not Delete to edit this room.")
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'room':room}
    return render(request,'base/delete.html',context)




@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)
    # print(request.method)
    if request.user != message.user:
        return HttpResponse("You are not Delete to edit this room.")
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context = {'obj':message}
    return render(request,'base/delete.html',context)