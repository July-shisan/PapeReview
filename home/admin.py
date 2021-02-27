from django.contrib import admin
from django.utils.translation import ugettext_lazy
# Register your models here.
from home.models import User, UploadFile, Challenge, BackFile
from django.http import HttpResponse, FileResponse
from django.urls import path
from django.utils.html import format_html
from django.shortcuts import render, redirect, reverse
from home.models import User, Challenge, UploadFile
from django.utils.encoding import escape_uri_path

class ChallengeAdmin(admin.ModelAdmin):
    # fields = ('chtype', 'bill', 'payment', 'hoster', )
    readonly_fields = ('requirment', 'bill', 'payment', 'hoster', 'release_time', 'uploadfile', 'backfile', 'download_link')
    exclude = ('award',)
    list_display = ('chId', 'chtype', 'bill', 'payment', 'hoster', 'uploadfile', 'release_time', 'backfile', 'download_link')
    # list_display_links = ('bill',)
    search_fields = ['hoster__username', 'uploadfile__name', 'bill', ]
    list_filter = ('chtype', 'hoster', 'release_time',)
    list_per_page = 10
    list_editable = ('chtype',)
    date_hierarchy = 'release_time'
    ordering = ('-release_time', 'chId')
    '''自定义actions'''
    actions = ['change_status0', 'change_status1', 'change_status2', 'change_status4']
    def change_status0(self, request, queryset):
        queryset.update(chtype=0)
    def change_status1(self, request, queryset):
        queryset.update(chtype=1)
    def change_status2(self, request, queryset):
        queryset.update(chtype=2)
    def change_status4(self, request, queryset):
        queryset.update(chtype=4)
    change_status0.short_description = "待处理所选订单"
    change_status1.short_description = "处理中所选订单"
    change_status2.short_description = "完成所选订单"
    change_status4.short_description = "系统取消所选订单"

    # add custom view to urls
    def get_urls(self):
        urls = super(ChallengeAdmin, self).get_urls()
        urls += [
            path('(?P<pk>\d+)$', self.download_file, name='applabel_modelname_download-file'),
        ]
        return urls
    # custom "field" that returns a link to the custom function
    def download_link(self, obj):
        # print('-------')
        # print(obj.pk)
        return format_html(
            '<a href="{}">Download file</a>',
            reverse('admin:applabel_modelname_download-file', args=[obj.pk])
        )
    download_link.short_description = "Download file"
    # add custom view function that downloads the file
    def download_file(self, request, pk):
        id = int(pk)
        task = Challenge.objects.get(chId=id)
        name = task.uploadfile.name
        file = open('upload/'+pk+'/'+name, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        # response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename={}'.format(escape_uri_path(name))
        # generate dynamic file content using object pk
        # response.write('whatever content')
        return response

# admin.site.register(Challenge, ChallengeAdmin)

class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('userId', 'email', 'register_time', 'profile')
    list_display = ('userId', 'username', 'status', 'email', 'register_time',)
    # list_display_links = ('bill',)
    search_fields = ['username', 'userId', 'email', 'status']
    list_filter = ('userId', 'username', 'status',)
    list_per_page = 10
    list_editable = ('status',)
    # date_hierarchy = 'release_time'
    ordering = ('-register_time', 'userId', )
    '''自定义actions'''
    actions = ['disable', 'enable']
    def disable(self, request, queryset):
        queryset.update(status=0)
    def enable(self, request, queryset):
        queryset.update(status=1)
    disable.short_description = '禁用所选用户'
    enable.short_description = '启用所选用户'
class UploadFileAdmin(admin.ModelAdmin):
    readonly_fields = ('path', 'size', 'upload_time', 'challenge')
    list_display = ('fileId', 'name', 'path', 'size', 'upload_time', 'challenge')
    # list_display_links = ('bill',)
    search_fields = ['name', 'challenge__chId']
    list_filter = ('upload_time',)
    list_per_page = 10
    # list_editable = ('chtype',)
    # date_hierarchy = 'release_time'
    ordering = ('-challenge', '-upload_time', )
class BackFileAdmin(admin.ModelAdmin):
    readonly_fields = ('size', 'path')
    list_display = ('fileId', 'name', 'path', 'size', 'upload_time', 'challenge')
    # list_display_links = ('bill',)
    search_fields = ['name', 'challenge__chId']
    list_filter = ('upload_time',)
    list_per_page = 10
    # list_editable = ('chtype',)
    # date_hierarchy = 'release_time'
    ordering = ('-challenge', '-upload_time', )

class MyAdminSite(admin.AdminSite):
    #网站标签页标题
    site_title = ugettext_lazy('后台管理')
    #网站标题
    site_header = ugettext_lazy('EDITOR后台管理')

my_adminsite = MyAdminSite()
my_adminsite.register(Challenge, ChallengeAdmin)
my_adminsite.register(User, UserAdmin)
my_adminsite.register(UploadFile, UploadFileAdmin)
my_adminsite.register(BackFile, BackFileAdmin)