from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import json

from .models import Post, User, Follow, Like

from django.core.paginator import Paginator

def removeLike(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like.objects.filter(user=user , post=post)
    like.delete()
    return JsonResponse({"message": "Like removed successfully"});

def addLike(request , post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    newLike = Like(user=user, post=post)
    newLike.save()
    return JsonResponse({"message": "Like added successfully"});


def index(request):
    allPosts = Post.objects.all().order_by("id").reverse()

    p = Paginator(allPosts, 2)
    pageNumber = request.GET.get('page')
    postOnPage = p.get_page(pageNumber)

    allLikes = Like.objects.all()

    whoUserLiked = []

    try:
        for like in allLikes:
            if like.user.id == request.user.id:
                whoUserLiked.append(like.post.id)
    except:
        whoUserLiked = []

    return render(request, "network/index.html" , {
        "postOnPage": postOnPage,
        "whoUserLiked": whoUserLiked
    })

def edit(request , post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.content = data["content"]
        edit_post.save()
        return JsonResponse({"message": "Change done successfully" , "data": data["content"]})

def newPost(request):
    if request.method == "POST":
        content = request.POST["post"]
        user = request.user
        post = Post(user=user , content=content)
        post.save()
        return HttpResponseRedirect(reverse("index"))

def profile(request, user_name):
    user = User.objects.get(username=user_name)
    allPosts = Post.objects.filter(user=user).order_by("id").reverse()

    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(followingUser=user)

    try:
        checkFollow = followers.filter(user=User.objects.get(pk=request.user.id))
        if len(checkFollow) != 0:
            isFollowing = True
        else:
            isFollowing = False
    except:
        isFollowing = False

    p = Paginator(allPosts, 2)
    pageNumber = request.GET.get('page')
    postOnPage = p.get_page(pageNumber)

    return render(request, "network/profile.html" , {
        "allPosts": allPosts,
        "postOnPage": postOnPage,
        "username":user_name,
        "following": following.count(),
        "followers":followers.count(),
        "isFollowing": isFollowing,
        "userProfile": user
    })

def following(request):
    curentUser = User.objects.get(pk=request.user.id)
    following = Follow.objects.filter(user=curentUser)
    allPosts = Post.objects.all().order_by("id").reverse()

    followingPosts = []

    for post in allPosts:
        for person in following:
            if post.user == person.followingUser:
                followingPosts.append(post)

    p = Paginator(followingPosts, 2)
    pageNumber = request.GET.get('page')
    postOnPage = p.get_page(pageNumber)

    return render(request, "network/following.html" , {
        "postOnPage": postOnPage
    })

def follow(request):
    userFollow = request.POST['userfollow']
    curentUser = User.objects.get(pk=request.user.id)
    userFollowData = User.objects.get(username=userFollow)
    f = Follow(user=curentUser , followingUser=userFollowData)
    f.save()
    userName = userFollowData.username
    return HttpResponseRedirect(reverse("profile", kwargs={"user_name":userName}))

def unfollow(request):
    userFollow = request.POST['userfollow']
    curentUser = User.objects.get(pk=request.user.id)
    userFollowData = User.objects.get(username=userFollow)
    f = Follow.objects.get(user=curentUser , followingUser=userFollowData)
    f.delete()
    userName = userFollowData.username
    return HttpResponseRedirect(reverse("profile", kwargs={"user_name":userName})) 

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
