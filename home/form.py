#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django import forms
from .models import User, Challenge, UploadFile
import datetime

class registerForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(registerForm, self).clean()
        return cleaned_data
    class Meta:
        model = User
        fields = {'username', 'password'}


class loginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = {'username', 'password'}


class uploadForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = {'file'}

class profileForm(forms.Form):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=False)
    profile = forms.CharField(required=False)
    def clean(self):
        cleaned_data = super(profileForm, self).clean()
        return cleaned_data

class noteForm(forms.Form):
    requirment = forms.CharField(required=False)
    def clean(self):
        cleaned_data = super(noteForm, self).clean()
        return cleaned_data