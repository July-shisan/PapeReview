import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse

from home.models import User, Challenge, UploadFile
from django.views.generic import View
from django.db import connection
from .form import registerForm, loginForm, profileForm, noteForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.paginator import Paginator
from CrowdPlat.settings import MEDIA_ROOT

import os
import docx
import re

# def home(request):
#     return render(request, 'home.html')
def get_corsor():
    return connection.cursor()

class homeView(View):
    def get(self, request):
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 5))
        challenge = Challenge.objects.all().order_by('-release_time')
        paginator = Paginator(challenge , per_page)
        page_object = paginator.page(page)
        data = {
            "page_object": page_object,
            "page_range": paginator.page_range,
            "title": "EDITOR",
            "challenge": challenge,
        }
        return render(request, 'home.html', context=data)


def egg(request):
    return render(request, '彩蛋.html')
def logout(request):
    request.session.flush()
    response = redirect(reverse('home'))
    response.delete_cookie('userId')
    response.delete_cookie('username')
    response.delete_cookie('password')
    messages.success(request, "已退出登录！")
    return response
# def profile(request, userId):
#     id = int(userId)
#     user = User.objects.get(pk=id)
#     hist_chal = user.challenge_set.all()
#     data = {
#         "title": "profile",
#         "user": user,
#         "history": hist_chal
#     }
#     return render(request, 'profile.html', context=data)
class profileView(View):
    def get(self, request):
        id = request.session.get('user_id')
        user = User.objects.get(pk=id)
        chall = user.challenge_set.all()
        pending = []
        processing = []
        finished = []
        self_cancel = []
        sys_cancel = []
        for challenge in chall:
            if challenge.chtype == 0:
                pending.append(challenge)
            elif challenge.chtype == 1:
                processing.append(challenge)
            elif challenge.chtype == 2:
                finished.append(challenge)
            elif challenge.chtype == 3:
                self_cancel.append(challenge)
            elif challenge.chtype == 4:
                sys_cancel.append(challenge)
        data = {
            "title": "profile",
            "user": user,
            "pending": pending,
            "processing": processing,
            "finished": finished,
            "self_cancel": self_cancel,
            "sys_cancel": sys_cancel,
        }
        return render(request, 'profile.html', context=data)
    # 更新个人信息
    def post(self, request):
        form = profileForm(request.POST or None)
        if form.is_valid():
            name = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            profile = form.cleaned_data.get('profile')
            id = request.session.get('user_id')
            user = User.objects.get(pk=id)
            user.username = name
            user.profile = profile
            user.email = email
            user.save()
            return redirect('/profile')
        else:
            print(form.errors.get_json_data())
            # messages.success(request, "信息填写错误!")
            return redirect('/profile')
class loginView(View):
    def get(self, request):
        data = {
            "title": "login"
        }
        return render(request, 'login.html', context=data)
    def post(self, request):
        next = request.GET.get('next', '')
        if next == '/login/' or next == '/register/' or len(next) == 0:
            next = '/'
        form = loginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = User.objects.filter(username=username, password=password).first()
            if user:
                if user.status == 0:
                    messages.success(request, "该用户已被禁用！")
                    return redirect(reverse('login'))
                request.session['user_id'] = user.userId
                # response = redirect(reverse('home'))
                response = HttpResponseRedirect(next)
                # response.set_cookie("userId", user.userId)
                # response.set_cookie("username", username)
                # response.set_cookie("password", password)
                return response
            else:
                print('用户名或密码错误')
                messages.success(request, "用户名或密码错误!")
                return redirect(reverse('login'))
        else:
            print(form.errors.get_json_data())
            messages.success(request, "用户名或密码错误!")
            return redirect(reverse('login'))
# 注册时用户名是否存在的验证函数
def register_verif(request):
    if request.method == "POST":
        name = request.POST.get('name')
        user = getUser(bytes(name, encoding='utf-8'))
        try:
            json.loads(user, strict=False)
        except Exception:
            # 无相同用户名
            return HttpResponse(None)
        else:
            msg = 'success'
            return HttpResponse(msg)
class registerView(View):
    def get(self, request):
        data = {
            "title": "register"
        }
        return render(request, 'register.html', context=data)
    def post(self, request):
        form = registerForm(request.POST or None)
        # form.register_time = datetime.datetime.now().strftime('%Y-%m-%d')
        if form.is_valid():
            form.save()
            messages.success(request, "注册成功，请登录！")
            return redirect(reverse('login'))
        else:
            errors = form.errors
            print(errors)
            messages.success(request, "填写信息无效！")
            return redirect(reverse('register'))

def upload(request):
    return render(request, 'upload.html')

def wordnumbers(request):
    if request.method == 'POST':
        f = request.FILES.get('file')
        userId = request.session.get('user_id')
        file = docx.Document(f)
        # count = 100
        count = 0
        for para in file.paragraphs:
            # n = len(str(para.text))
            count_en = 0
            count_zh = 0
            s = para.text
            zh = []
            for c in s:
                if u'\u4e00' <= c <= u'\u9fff':
                    # 包含中文
                    zh.append(c)
                    count_zh += 1
            if count_zh > 0:
                # 包含中文
                for i in zh:
                    s = s.replace(i, ' ')
                count_en = len([i for i in s.split(' ') if i])
            else:
                # 全是英文
                # 替换字符为空格
                r = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'
                s = re.sub(r, ' ', s)
                count_en = len([i for i in s.split(' ') if i])
            count += count_zh
            count += count_en
        # 创建订单
        user = User.objects.get(pk=userId)
        bill = float(count)/1000
        challenge = Challenge(chtype=0, bill=bill, hoster=user)
        challenge.save()
        # Challenge.objects.create(chtype=0, award=bill, hoster=user)
        # 创建文件对象
        name = str(f)
        size = len(f)
        path = MEDIA_ROOT + name
        UploadFile.objects.create(file=f, name=name, size=size, path=path, challenge=challenge)
        return HttpResponse(count)
def task(request, taskId):
    if request.method == "GET":
        id = int(taskId)
        task = Challenge.objects.get(chId=id)
        data = {
            "task": task,
        }
        return render(request, 'task.html', context=data)
    if request.method == "POST":
        form = noteForm(request.POST or None)
        id = int(taskId)
        task = Challenge.objects.get(chId=id)
        if form.is_valid():
            requirment = form.cleaned_data.get('requirment')
            task.requirment = requirment
            task.save()
            data = {
                "task": task,
            }
            return render(request, 'task.html', context=data)
        else:
            print(form.errors.get_json_data())
            data = {
                "task": task,
            }
            # messages.success(request, "信息填写错误!")
            return render(request, 'task.html', context=data)
def cancelIt(request):
    if request.method == "POST":
        chid = request.POST.get('chid')
        # 获得challenge 并改变状态
        order = Challenge.objects.get(pk=chid)
        order.chtype = 3
        order.save()
        return HttpResponse('success')
