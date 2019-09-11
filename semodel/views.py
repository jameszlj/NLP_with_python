# -*- coding: utf-8 -*-
import os

from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.views.decorators.csrf import requires_csrf_token, csrf_exempt
from django.conf import settings
from models import User
from pyltp import SentenceSplitter
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import SementicRoleLabeller
from pyltp import NamedEntityRecognizer
from pyltp import Parser


import sys
reload(sys)
sys.setdefaultencoding('utf8')


#句子分词
#segmentor = Segmentor()  # 初始化实例
#segmentor.load('E:\\python2.7 install\\pyltp-master\\ltp_data\\cws.model')  # 加载模型
# segmentor.load_with_lexicon('E:\\python2.7 install\\pyltp-master\\ltp_data\\cws.model','E:\\python2.7 install\\pyltp-master\\ltp_data\\cws.txt')
#segmentor.load_with_lexicon('/mnt/hgfs/ubuntu-share/pyltp-master/ltp_data/cws.model','/mnt/hgfs/ubuntu-share/pyltp-master/ltp_data/cws.txt')

#count=10

#POSTAGGER= Postagger()
#settings.POSTAGGER.load_with_lexicon('/mnt/hgfs/ubuntu-share/pyltp-master/ltp_data/pos.model','/mnt/hgfs/ubuntu-share/pyltp-master/ltp_data/pos.txt')
LTP_DATA_DIR = 'D:\\LTP\\ltp_data'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`pos.model`
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
srl_model_path = os.path.join(LTP_DATA_DIR, 'srl')  # 语义角色标注模型目录路径，模型目录为`srl`。注意该模型路径是一个目录，而不是一个文件。




#表单
class UserForm(forms.Form):
     intext = forms.CharField(label='语句',max_length=500)

#分析
@csrf_exempt
def analyse(req):
    if req.method == 'POST':
        print "11111111111111"
        #uf = UserForm(req.POST)
        print "22222222222222"
        intext = "我是中国人"
        #pageNumber = request.POST.get('pageNumber',1)
        print req.POST
        #intext = req.POST["intext"][0]

        print req.POST["intext"]
        intext = req.POST["intext"].encode('utf-8', 'ignore')
        #print req.POST["intext"][0]
        #intext = uf.cleaned_data['intext']
        outtext = '{"result":['
        outtext += sentement(intext) +']}'
        return HttpResponse(outtext)


        #return HttpResponse('input unsuccess!')
        '''
        if uf.is_valid():
            print "33333333333333333"
            #获得表单数据
            intext = uf.cleaned_data['intext']
            #intext.decode("gbk").encode("UTF-8")
            outtext = '{"result":['
            outtext += sentement(intext) +']}'
            return HttpResponse(outtext)
        else:
            return HttpResponse('input unsuccess!')
        '''
    else:
        uf = UserForm()
    #return render_to_response('regist.html',{'uf':uf}, context_instance=RequestContext(req))
    return render_to_response('semodel/analyse.html',{'uf':uf, 'layout':'vertical', 'title':'自然语义分析 语义分析'})

@csrf_exempt
def word_class_analyse(req):
    if req.method == 'POST':
        #print '-----------word_class_analyse START -----\r\n'
        intext = req.POST["intext"].encode('utf-8', 'ignore')

        # sentence = splitter(intext)
        words = segmentor(intext)
        tags = posttagger(words)

        #print '-----------word_class_analyse END -----\r\n'
        outtext = '{"result":['
        for word,tag in zip(words,tags):
            # print word+'/'+tag + '\r\n'
            outtext += '{"tag":"'+"%s" % tag+'",'
            outtext += '"content"'+':"' + word +'"},'

        outtext = outtext.rstrip(',') + ']}'

        response = HttpResponse(outtext)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST"

        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
        return response

@csrf_exempt
#命名识别
def name_entity_recognize(req):
    if req.method == 'POST':
        #print '-----------word_class_analyse START -----\r\n'
        intext = req.POST["intext"].encode('utf-8', 'ignore')

        words = segmentor(intext)
        tags = posttagger(words)

        recognizer = NamedEntityRecognizer()
        # recognizer.load('/usr/local/src/ltp_data/ner.model')
        recognizer.load(ner_model_path)
        #recognizer = settings.RECOGNIZER
        netags = recognizer.recognize(words, tags)  # 命名实体识别

        outtext = '{"result":['
        for word,tag in zip(words,netags):
            # print word+'/'+tag + '\r\n'
            outtext += '{"tag":"'+"%s" % tag+'",'
            outtext += '"content"'+':"' + word +'"},'

        outtext = outtext.rstrip(',') + ']}'

        response = HttpResponse(outtext)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST"

        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
        return response

@csrf_exempt
#依存句法分析
def dependency_parser(req):
    if req.method == 'POST':
        #print '-----------word_class_analyse START -----\r\n'
        intext = req.POST["intext"].encode('utf-8', 'ignore')

        words = segmentor(intext)
        tags = posttagger(words)

        parser = Parser() # 初始化实例
        # parser.load('/usr/local/src/ltp_data/parser.model')  # 加载模型
        parser.load(par_model_path)  # 加载模型
        arcs = parser.parse(words, tags)  # 句法分析
        #print "依存语义分析:\n"
        #print "\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs)

        outtext = '{"result":['

        for word, arc in zip(words, arcs):

            outtext += '{"content":"'+"%s" % word+'",'
            outtext += '"head"'+':' +"%d" % (arc.head -1) +','
            outtext += '"relate"'+':"' +"%s" % arc.relation +'"},'

        outtext = outtext.rstrip(',') + ']}'

        parser.release()  # 释放模型

        response = HttpResponse(outtext)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST"

        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
        return response

#文本分句
def splitter(document):
    sentence = SentenceSplitter.split(document)  # 分句
    #print '\n'.join(sentence)
    return sentence

#句子分词
def segmentor(sentence):
    #segmentor = Segmentor()  # 初始化实例
    #segmentor.load('E:\\python2.7 install\\pyltp-master\\ltp_data\\cws.model')  # 加载模型
   # segmentor.load_with_lexicon('E:\\python2.7 install\\pyltp-master\\ltp_data\\cws.model','E:\\python2.7 install\\pyltp-master\\ltp_data\\cws.txt')
    #segmentor.load_with_lexicon('/mnt/hgfs/ubuntu-share/pyltp-master/ltp_data/cws.model','/mnt/hgfs/ubuntu-share/pyltp-master/ltp_data/cws.txt')

    segmentor = Segmentor()
    segmentor.load_with_lexicon(cws_model_path,'D:\\LTP\\ltp_data\\cws.txt')
    #SEGMENTOR.load_with_lexicon('/usr/local/src/ltp_data/cws.model','/usr/local/src/ltp_data/cws.txt')
    words = segmentor.segment(sentence)  # 分词
    #默认可以这样输出

    print settings.STATIC_URL

    print "-----:"
    print '\n'.join(words)

    segmentor.release()  # 释放模型
    return words

#词性标注
def posttagger(words):
    postagger = Postagger() # 初始化实例
    #postagger.load('E:\\python2.7 install\\pyltp-master\\ltp_data\\pos.model')  # 加载模型
    postagger.load_with_lexicon(pos_model_path,'D:\\LTP\\ltp_data\\pos.txt')

    #postagger = settings.POSTAGGER
    #if settings.POSTAGGER is None:
    #    settings.POSTAGGER = Postagger()
    #    settings.POSTAGGER.load_with_lexicon('/mnt/hgfs/ubuntu-share/pyltp-master/ltp_data/pos.model','/mnt/hgfs/ubuntu-share/pyltp-master/ltp_data/pos.txt')


    #postagger  = settings.POSTAGGER


    postags = postagger.postag(words)  # 词性标注
    print "词性标注:\n"
    for word,tag in zip(words,postags):
        print word+'/'+tag

    postagger.release()  # 释放模型
    return postags

#命名识别
def ner(words, postags):
    recognizer = NamedEntityRecognizer()
    # recognizer.load('/usr/local/src/ltp_data/ner.model')
    recognizer.load(ner_model_path)
    #recognizer = settings.RECOGNIZER
    netags = recognizer.recognize(words, postags)  # 命名实体识别
    print "命名识别:\n"
    for word, ntag in zip(words, netags):
        print word + '/' + ntag

    recognizer.release()  # 释放模型
    return netags

#依存语义分析
def parse(words, postags):
    parser = Parser() # 初始化实例
    # parser.load('/usr/local/src/ltp_data/parser.model')  # 加载模型
    parser.load(par_model_path)  # 加载模型
    arcs = parser.parse(words, postags)  # 句法分析
    print "依存语义分析:\n"
    print "\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs)

    i = 0
    for word, arc in zip(words, arcs):
        #print word + "\t".join("%d:%s" % (arc.head, arc.relation))
        print "%d" % i + "|" + word + ("|%d|%s" % (arc.head-1, arc.relation))
        i = i+1

    parser.release()  # 释放模型
    return arcs

#角色标注
def role(words, postags, netags, arcs):
    labeller = SementicRoleLabeller() # 初始化实例
    # labeller.load('/usr/local/src/ltp_data/srl')  # 加载模型
    labeller.load(srl_model_path)  # 加载模型
    roles = labeller.label(words, postags, netags, arcs)  # 语义角色标注
    """
    #arg.name 表示语义角色关系
    #arg.range.start 表示起始词位置
    #arg.range.end 表示结束位置
    roletype = {'C-A0':'施事','A0':'施事','A1':'受事','A2':'间接对象','A3':'直接目标','A4':'直接方法','A5':'其它','ADV':'附词','BNE':'受益人'
        , 'CND': '条件','DIR':'方向','DGR':'程度','EXT':'扩展','FRQ':'频率','LOC':'地点','MNR':'方式','PRP':'目的或原因'
        , 'TMP': '时间', 'TPC': '主题', 'CRD': '并列', 'PRD': '谓词', 'PSR': '持有者', 'PSE': '被持有','DIS': '转折'}
    postype = {'A0':'施事','A1':'受事','A2':'间接对象','A3':'直接目标','A4':'直接方法','A5':'其它','ADV':'附词','BNE':'受益人'
        , 'CND': '条件','DIR':'方向','DGR':'程度','EXT':'扩展','FRQ':'频率','LOC':'地点','MNR':'方式','PRP':'目的或原因'
        , 'TMP': '时间', 'TPC': '主题', 'CRD': '并列', 'PRD': '谓词', 'PSR': '持有者', 'PSE': '被持有'}
    for role in roles:
        #print role.index, "".join(["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments])

        outstr = ""
        for arg in role.arguments:
            block = ''

            for num in range(arg.range.start, arg.range.end+1):
                block = block + words[num]+'[%d-%s]'%(num,postags[num])
            outstr = outstr + roletype[arg.name] + "(%s);" % block
        print '%d-%s'%(role.index,words[role.index])+ ":"+outstr
    """
    labeller.release()  # 释放模型
    return roles

#情感标注
def emotion(words, postags, arcs):
    outtext = ""
    i = 0
    for word, arc,tag in zip(words,arcs,postags):
        #print "%d" % i + "|" + word + ("|%s|%s" % (tag,arc.relation))
        #outtext += "%d" % i + "|" + word + ("|%s|%s" % (tag,arc.relation))+"##"
        outtext += '{"order":'+"%d" % i+','
        outtext += '"content"'+':"' + word + ("|%s|%d|%s" % (tag,arc.head,arc.relation))+'"},'
        i = i + 1
    outtext = outtext.rstrip(',')
    return outtext

def sentement(document):

    # sentence = splitter(document)
    sentence = document
    words = segmentor(sentence)
    tags = posttagger(words)

    arcs = parse(words, tags)
    outtext = emotion(words, tags, arcs)
    return outtext 
