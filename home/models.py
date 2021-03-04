from django.db import models
from datetime import datetime
from CrowdPlat.settings import MEDIA_ROOT
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.
class Person(models.Model):
    personId = models.AutoField(primary_key=True)
    p_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100, null=False)
    age = models.IntegerField(default=1)
    email = models.EmailField(null=True)
    frame = models.IntegerField(default=50)
    register_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True

class User(models.Model):
    userId = models.AutoField(primary_key=True)
    status = models.BooleanField(default=1)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100, null=False)
    email = models.EmailField(null=True)
    profile = models.TextField(null=True)
    register_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'user'
    def __str__(self):
        return self.username

class Challenge(models.Model):
    chId = models.AutoField(primary_key=True)
    chtype_choices = ((0, '待处理'), (1, '处理中'), (2, '已完成'), (3, '已取消'), (4, '系统取消'))
    chtype = models.IntegerField(choices=chtype_choices, default=0, validators=[MaxValueValidator(4), MinValueValidator(0)])
    requirment = models.TextField(null=True)
    feedback = models.TextField(null=True)
    award = models.IntegerField(default=0)
    bill = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    payment = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    release_time = models.DateTimeField(auto_now_add=True)
    hoster = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = 'challenge'
    def __str__(self):
        return str(self.chId)
    # def __init__(self, a,b,c,d,e,f,g,h,i):
    #     if self.award == 1:
    #         self.chtype = 2
    # def save(self, *args, **kwargs):
    #     """
    #     Saves model and set initial state.
    #     """
    #     super(Challenge, self).save(*args, **kwargs)
    #     if self.backfile:
    #         self.chtype = 2

def upload_to(instance, filename):
    nowtime = datetime.now()
    return '/'.join([MEDIA_ROOT, str(instance.challenge.chId), filename])
class UploadFile(models.Model):
    fileId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    file = models.FileField(upload_to=upload_to)
    size = models.DecimalField(max_digits=10, decimal_places=0)
    path = models.CharField(max_length=500)
    upload_time = models.DateTimeField(auto_now_add=True)
    # auther = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    challenge = models.OneToOneField(Challenge, on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = 'file'
    def __str__(self):
        return self.name

class BackFile(models.Model):
    fileId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    file = models.FileField(upload_to=upload_to)
    size = models.DecimalField(max_digits=10, decimal_places=0, null=True)
    path = models.CharField(max_length=500, null=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True)
    # auther = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    challenge = models.OneToOneField(Challenge, on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = 'backfile'
    def __str__(self):
        return self.name
    # def __init__(self):
    #     self.challenge.chtype = 2
    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        self.challenge.chtype = 2
        self.challenge.save()
        super(BackFile, self).save(*args, **kwargs)

class Order(models.Model):
    order_number = models.CharField(max_length=64)
    status_choices = ((0, '未支付'), (1, '已支付'))
    order_status = models.IntegerField(choices=status_choices, default=0)
    bill = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    challenge = models.OneToOneField(Challenge, on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = 'order'
    def __str__(self):
        return str(self.order_status)



