# -*- coding: utf-8 -*-
from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext, loader
from django import forms
from django.views.decorators.csrf import requires_csrf_token, csrf_exempt
from django.conf import settings

from .SentimentAnalysis import SentimentAnalysis
from .forms import SentimentAnalyseForm
from semodel import views as semodelView

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json

#句子分词
#segmentor = Segmentor()  # 初始化实例
#segmentor.load('E:\\python2.7 install\\pyltp-master\\ltp_data\\cws.model')  # 加载模型
# segmentor.load_with_lexicon('E:\\python2.7 install\\pyltp-master\\ltp_data\\cws.model','E:\\python2.7 install\\pyltp-master\\ltp_data\\cws.txt')
#segmentor.load_with_lexicon('/mnt/hgfs/ubuntu-share/pyltp-master/ltp_data/cws.model','/mnt/hgfs/ubuntu-share/pyltp-master/ltp_data/cws.txt')

#count=10

#POSTAGGER= Postagger()
#settings.POSTAGGER.load_with_lexicon('/mnt/hgfs/ubuntu-share/pyltp-master/ltp_data/pos.model','/mnt/hgfs/ubuntu-share/pyltp-master/ltp_data/pos.txt')

#分析
@csrf_exempt
def analyse(req):

    if req.method == 'POST':
        #pageNumber = request.POST.get('pageNumber',1)

        stmts = req.POST["intext"].strip().encode('utf-8', 'ignore')
        kw = req.POST["kw"].strip().encode('utf-8', 'ignore')
        kwList = kw.split('+')

        semantiResult = '[' + semodelView.sentement(stmts) + ']'
        semantiList = json.loads(semantiResult)

        analyseArr = dict()
        for k in range(len(semantiList)):
           analyseArr[k] = "%d|%s" % ( semantiList[k]['order'], semantiList[k]['content'])

        sentimentUtils = SentimentAnalysis(settings.BASE_DIR)
        # print " \r\n 48 : ", analyseArr
        qp = sentimentUtils.relateSentiment(analyseArr, kwList[0])
        qn = sentimentUtils.relateSentiment(analyseArr, kwList[0], -1)

        ps = sum(qp.values())
        ns = sum(qn.values())

        if( abs(ps) > abs(ns) and ps < 0 ):
            ns = abs(ps) + ns
            ps = 0
        elif( abs(ns) > abs(ps) and ns < 0 ):
            ps = abs(ns) + ps
            ns = 0
        elif( ns < 0 ):
            ps += abs( ns )
            ns = 0
        elif( ps < 0 ):
            ns += abs( ps )
            ps = 0

        ret = dict()
        ret["result"] = [ {"qp": ps, "qn": ns} ]

        response = HttpResponse(json.dumps(ret))
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST"

        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
        return response
    else:
        saf = SentimentAnalyseForm()
    return render_to_response('sentiment/analyse.html',{'saf':saf, 'layout':'vertical', 'title':'自然语义分析 情感值分析'})