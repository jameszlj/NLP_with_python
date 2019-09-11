# -*- coding: utf-8 -*-
import os

LTP_DATA_DIR = 'D:\\LTP\\ltp_data'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`pos.model`
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
srl_model_path = os.path.join(LTP_DATA_DIR, 'srl')  # 语义角色标注模型目录路径，模型目录为`srl`。注意该模型路径是一个目录，而不是一个文件。

from pyltp import SentenceSplitter
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SementicRoleLabeller


# 分句，也就是将一片文本分割为独立的句子
def sentence_splitter(sentence='人生苦短。我用python。你呢？'):
    sents = SentenceSplitter.split(sentence)  # 分句
    print ('\n'.join(sents))


# 分词
def segmentor(sentence='我是中国人'):
    segmentor = Segmentor()  # 初始化实例
    segmentor.load(cws_model_path)  # 加载模型
    words = segmentor.segment(sentence)  # 分词
    # 默认可以这样输出
    print ('\t'.join(words))
    # 可以转换成List 输出
    words_list = list(words)
    segmentor.release()  # 释放模型
    return words_list


def posttagger(words):
    postagger = Postagger()  # 初始化实例
    postagger.load(pos_model_path)  # 加载模型
    postags = postagger.postag(words)  # 词性标注
    for word, tag in zip(words, postags):
        print (word + '/' + tag)
    postagger.release()  # 释放模型
    return postags


# 命名实体识别
def ner(words, postags):
    recognizer = NamedEntityRecognizer()  # 初始化实例
    recognizer.load(ner_model_path)  # 加载模型
    netags = recognizer.recognize(words, postags)  # 命名实体识别
    for word, ntag in zip(words, netags):
        print (word + '/' + ntag)
    recognizer.release()  # 释放模型
    return netags


# 依存语义分析
def parse(words, postags):
    parser = Parser()  # 初始化实例
    parser.load(par_model_path)  # 加载模型
    arcs = parser.parse(words, postags)  # 句法分析
    print ("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
    parser.release()  # 释放模型
    return arcs


# 角色标注
def role_label(words, postags, netags, arcs):
    labeller = SementicRoleLabeller()  # 初始化实例
    labeller.load(srl_model_path)  # 加载模型
    roles = labeller.label(words, postags, netags, arcs)  # 语义角色标注
    for role in roles:
        print (role.index, "".join(
            ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))
    labeller.release()  # 释放模型


# 测试分句子
print('******************测试将会顺序执行：**********************')
sentence_splitter()
print('###############以上为分句子测试###############')
# 测试分词
words = segmentor()
print('###############以上为分词标注测试###############')
# 测试标注
tags = posttagger(words)
print('###############以上为词性标注测试###############')
# 命名实体识别
netags = ner(words, tags)
print('###############以上为命名实体识别测试###############')
# 依存句法识别
arcs = parse(words, tags)
print('###############以上为依存句法测试###############')
# 角色标注
roles = role_label(words, tags, netags, arcs)
