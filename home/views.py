import datetime
import hashlib
from django.http import HttpResponse, FileResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.utils.encoding import escape_uri_path

from home.models import User, Challenge, UploadFile, Order
from django.views.generic import View
from django.db import connection
from .form import registerForm, loginForm, profileForm, noteForm, payForm
# from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.paginator import Paginator
from CrowdPlat.settings import MEDIA_ROOT
from wechatpy.pay import WeChatPay

from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.domain.AlipayTradePrecreateModel import AlipayTradePrecreateModel
from alipay.aop.api.request. AlipayTradePrecreateRequest import AlipayTradePrecreateRequest
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from urllib.parse import urlencode
# from alipay import AliPay
import uuid
import time
import requests
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
def qqtest(request):
    params = {
        'response_type':'code',
        'client_id':'101938750',
        'redirect_url':'http://212.64.64.87:8000/gh',
        'state':'guohua',
    }
    # return render(request, '彩蛋.html')
    return redirect('https://graph.qq.com/oauth2.0/authorize?'+urlencode(params))

def egg(request):
    return render(request, '彩蛋.html')
def wxtest(request):
    # 微信认证
    token = 'Unique'
    # print(token)
    if request.method == 'GET':
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        # echostr = request.GET.get('echostr')
        # if not wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
        #     return HttpResponseBadRequest('Verify Failed')
        # else:
        # return HttpResponse('yes')
        # print(echostr)
        # return HttpResponse(request.GET.get('echostr', ''), content_type='text/plain')
        try:
            tmp_str = hashlib.sha1(''.join(sorted([token, timestamp, nonce])).encode('utf-8')).hexdigest()
            if tmp_str == signature:
                return HttpResponse(request.GET.get('echostr', ''), content_type='text/plain')
            else:
                return HttpResponse('Verify Failed')
        except Exception:
            return HttpResponse('error')


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
def download(request, taskId):
    id = int(taskId)
    task = Challenge.objects.get(chId=id)
    name = task.backfile.name
    # print(task.backfile.file)
    # file = open('upload/'+taskId+'/'+name, 'rb')
    path = str(task.backfile.file)
    p,f = os.path.split(path)
    file = open(path, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    # response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename={}'.format(escape_uri_path(f))
    return response
def wordnumbers(request):
    if request.method == 'POST':
        f = request.FILES.get('file')
        userId = request.session.get('user_id')
        if f:
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
            bill = float(count) / 1000
            challenge = Challenge(chtype=0, bill=bill, hoster=user)
            # print(challenge.chId)
            challenge.save()
            request.session['chid'] = challenge.chId
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

WECHAT = {
        'APPID': 'wx8397f8696b538317',                                           # 小程序ID
        'APPSECRET': '66bf76b58d00cb51f4596bd33ba212f3',			                        # 小程序SECRET
        'MCH_ID': '1473426802',                                         # 商户号
        'TOTAL_FEE': '1',                                           # 总金额
        'SPBILL_CREATE_IP': '212.64.64.87',                            # 终端IP
        'NOTIFY_URL': 'http://212.64.64.87:8000/wxpayNotify',          # 通知地址
        'TRADE_TYPE': 'JSAPI',                                      # 交易类型
        'MERCHANT_KEY': 'T6m9iK73b0kn9g5v426MKfHQH7X8rKwb',                             # 商户KEY
        'BODY': '商品描述',                                           # 商品描述
}
def get_user_info(js_code):
    """
    使用 临时登录凭证code 获取 session_key 和 openid 等
    支付部分仅需 openid，如需其他用户信息请按微信官方开发文档自行解密
    """
    req_params = {
        'appid': WECHAT['APPID'],
        'secret': WECHAT['APPSECRET'],
        'js_code': js_code,
        'grant_type': 'authorization_code',
    }
    user_info = requests.get('https://api.weixin.qq.com/sns/jscode2session', params=req_params, timeout=3, verify=False)
    return user_info.json()
def wxpay(request):
    """
    通过小程序前端 wx.login() 接口获取临时登录凭证 code
    将 code 作为参数传入，调用 get_user_info() 方法获取 openid
    """
    code = request.GET.get("code", None)
    openid = get_user_info(code)['openid']
    # openid = '1234'

    pay = WeChatPay(WECHAT['APPID'], WECHAT['MERCHANT_KEY'], WECHAT['MCH_ID'])
    order = pay.order.create(
        trade_type=WECHAT['TRADE_TYPE'],  # 交易类型，小程序取值：JSAPI
        body=WECHAT['BODY'],  # 商品描述，商品简单描述
        total_fee=WECHAT['TOTAL_FEE'],  # 标价金额，订单总金额，单位为分
        notify_url=WECHAT['NOTIFY_URL'],  # 通知地址，异步接收微信支付结果通知的回调地址，通知url必须为外网可访问的url，不能携带参数。
        user_id=openid  # 用户标识，trade_type=JSAPI，此参数必传，用户在商户appid下的唯一标识。
    )
    wxpay_params = pay.jsapi.get_jsapi_params(order['prepay_id'])

    return HttpResponse(json.dumps(wxpay_params))

def wxpayNotify(request):
    _xml = request.body
    # 拿到微信发送的xml请求 即微信支付后的回调内容
    xml = str(_xml, encoding="utf-8")
    print("xml", xml)
    return_dict = {}
    tree = et.fromstring(xml)
    # xml 解析
    return_code = tree.find("return_code").text
    try:
        if return_code == 'FAIL':
            # 官方发出错误
            return_dict['message'] = '支付失败'
            # return Response(return_dict, status=status.HTTP_400_BAD_REQUEST)
        elif return_code == 'SUCCESS':
            # 拿到自己这次支付的 out_trade_no
            _out_trade_no = tree.find("out_trade_no").text
            # 这里省略了 拿到订单号后的操作 看自己的业务需求
    except Exception as e:
        pass
    finally:
        return HttpResponse(return_dict, status=status.HTTP_200_OK)

def ali_pay():
    # 为阿里支付实例化一个配置信息对象
    alipay_config = AlipayClientConfig(sandbox_debug=True)
    # 初始化各种配置信息
    # 阿里提供服务的接口
    alipay_config.server_url = "https://openapi.alipaydev.com/gateway.do"
    # 申请的沙箱环境的app_id
    alipay_config.app_id = "2021000117615932"
    # 商户的私钥
    with open("keys/应用私钥2048.txt") as f:
        alipay_config.app_private_key = f.read()
    # 阿里的公钥
    with open("keys/应用公钥2048.txt") as f:
        alipay_config.alipay_public_key = f.read()
    # 实例化一个支付对象并返回
    alipay_client = DefaultAlipayClient(alipay_client_config=alipay_config)
    return alipay_client
class PayView(APIView):
    def post(self, request):
        # 实例化订单
        chid = request.session.get('chid')
        # chid = 6
        if not chid:
            return HttpResponse("请先上传文件！")
        challenge = Challenge.objects.get(pk=chid)
        form = payForm(request.POST or None)
        if form.is_valid():
            challenge.requirment = form.cleaned_data.get('note')
            challenge.save()
            orderid = request.session.get('orderid')
            method = form.cleaned_data.get('method')
            if not orderid:
                order_number = str(uuid.uuid4())
                bill = challenge.bill
                order = Order(order_number=order_number, order_status=0, bill=bill, challenge=challenge)
                # print(challenge.chId)
                order.save()
                request.session['orderid'] = order.id
            if method == 'alipay':
                model = AliPay(chid)
                # 实例化一个请求对象
                client = ali_pay()
                request = AlipayTradePagePayRequest(biz_model=model)
                # get请求 用户支付成功后返回的页面请求地址
                request.return_url = "http://212.64.64.87:8000/alipay_handler"
                # post请求 用户支付成功通知商户的请求地址
                request.notify_url = "http://212.64.64.87:8000/alipay_handler"
                # 利用阿里支付对象发一个获得页面的请求 参数是request
                response = client.page_execute(request, http_method="GET")
                return redirect(response)
            else:
                return HttpResponse("请选择支付宝支付")
        else:
            return HttpResponse("error")
def AliPay(chid):
    # def get(self, request):
    #     return render(request, "pay.html")
    # 生成支付宝自带页面的API
    # 实例化订单
    challenge = Challenge.objects.get(pk=chid)
    # 得到阿里支付的实例化对象
    # 为API生成一个模板对象 初始化参数用的
    model = AlipayTradePagePayModel()
    # 订单号
    model.out_trade_no = "pay" + str(time.time())
    # 金额
    # model.total_amount = challenge.bill
    model.total_amount = str(challenge.bill)
    # 商品标题
    model.subject = str(challenge.chId)
    # 商品详细内容
    model.body = str(challenge.uploadfile.name)
    # 销售产品码，与支付宝签约的产品码名称
    model.product_code = "FAST_INSTANT_TRADE_PAY"
    return model

class PayHandlerView(APIView):
    def get(self, request):
        # return_url的回调地址
        # 付款成功
        chid = request.session.get('chid')
        orderid = request.session.get('orderid')
        challenge = Challenge.objects.get(pk=chid)
        order = Order.objects.get(pk=orderid)
        challenge.payment = 1
        order.order_status = 1
        challenge.save()
        order.save()
        print(request.data)
        # 用户支付成功之后回到哪
        id = request.session.get('user_id')
        # request.session.flush()
        # request.session['user_id'] = id
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
        # return HttpResponse("return_url测试")
    def post(self, request):
        print(request.data)
        # 用户支付成功 在这里修改订单状态以及优惠券贝里等等情况
        return HttpResponse("notify_url")