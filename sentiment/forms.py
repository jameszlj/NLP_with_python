# -*- coding: utf-8 -*-
from django import forms

class SentimentAnalyseForm(forms.Form):
	'''
	情感分析表单
	'''
	stmts = forms.CharField(
		label=u'分析文本',
		max_length=500,
		widget=forms.Textarea(
		    attrs={
		        'title': '',
		    }
		),
	)
	kw = forms.CharField(label=u'关键词',max_length=500)