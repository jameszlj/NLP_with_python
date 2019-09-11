# -*- coding: utf-8 -*-
"""
CUSTOM FUNCTION
"""
import re


class SentimentAnalysis():
    '''
	情感分析
	'''
    DICTIONARY_DIR = ''
    POSITIVE = ''
    NEGATIVE = ''
    PNI = ''
    PPI = ''
    QNI = ''
    QPI = ''
    COJ = ''
    DEG = ''
    SHIFT = ''

    def __init__(self, base_dir):
        SentimentAnalysis.DICTIONARY_DIR = base_dir + '/sentiment/assets/dictionary/'

    def getlines(self, file_name):
        lines = []

        f = open(file_name)
        for line in f.readlines():
            line = unicode(line.strip(), 'utf-8')

            if not len(line):
                continue
            lines.append(line)

        return lines

    def getstmt(self, content):

        lines = []
        if content:
            # 多个单一 分隔符 时 ,"[]"与 "|"的 效果是一样的,但是 请注意 使用 “|”时 mouxie某些字符 需要转义
            lines = re.split(r'[。|？|！|……|~|！！！|。。|\.|！！]', content)

            for index in range(len(lines)):
                lines[index] = lines[index].strip()
                if not len(lines[index]):
                    del lines[index]
        return lines

    def geteval(self, stmt, words):
        sum_ratio = 0
        for s in stmt:

            ct = 0
            for w in words:
                if s.find(w) != -1:
                    ct += 1

            sum_ratio += ct / len(unicode(s, 'utf-8'))

        return len(stmt) > 0 and (sum_ratio / len(stmt)) or 0

    def getfromini(self, param_file):
        '''
		读取ini的语言系数
		返回一个字典，例如：{"非常":1.1,"很":1.1} 以词组为键，系数为值
		'''
        arr = self.getlines(param_file)
        dic = dict()
        d = 0

        regex = ur'\[(.+)\]'
        for e in arr:
            match = re.search(regex, e)

            if match:
                d = match.group(1)
                continue

            dic[e] = d

        return dic

    def getwords(self, positive):

        if positive == 1:
            if not SentimentAnalysis.POSITIVE:
                SentimentAnalysis.POSITIVE = self.getlines(SentimentAnalysis.DICTIONARY_DIR + 'positive.txt')
                return SentimentAnalysis.POSITIVE

        else:
            if not SentimentAnalysis.NEGATIVE:
                SentimentAnalysis.NEGATIVE = self.getlines(SentimentAnalysis.DICTIONARY_DIR + 'negative.txt')
            return SentimentAnalysis.NEGATIVE

    def getrelp(self, param_words=[], k=''):
        '''
		把语句拆分成以词性为键的数组,单个句子的所有词组作为一个元素
		如：[{"n":[[4, "城市""]], "v":[[5, "上班"]]}]
		'''
        word_arr = param_words
        data = dict()
        class_arr = dict()
        stat_arr = dict()
        inc_arr = dict()
        si = 0

        for r in range(len(word_arr)):
            eArr = word_arr[r].strip().split('|')
            if not data.has_key(si):
                stat_arr[si] = u''
                data[si] = dict()
            if data[si].has_key(eArr[2]):
                data[si][eArr[2]].append([r, eArr[1]])
            else:
                data[si][eArr[2]] = [[r, eArr[1]]]

            if class_arr.has_key(si):
                class_arr[si].append(eArr[2])  # 词性
            else:
                class_arr[si] = [eArr[2]]  # 词性

            stat_arr[si] += eArr[1]  # 字符

            if eArr[2] == 'wp':
                si += 1

        class_n = ('n', 'j', 'r', 'ni', 'nl', 'ns', 'nt', 'nz', 'nd', 'nh', 'ws')

        for r in range(len(class_arr)):  # r 行数
            c = class_arr[r]
            inc_arr[r] = 0  # 包含或不包含初始化

            if stat_arr[r].find(k) != -1:  # 显性包含关键字
                inc_arr[r] = 1
            else:  # 隐性
                ni = vi = -1  # 记录v和n的位置

                for rk in range(len(c)):  # row
                    rv = c[rk]

                    if ni == -1 and rv in class_n:
                        ni = rk

                    if vi == -1 and rv == 'v':
                        vi = rk

                if vi < ni:  # 隐性：主语与上个分句一致
                    if inc_arr.has_key(r - 1) and inc_arr[r - 1] == 1:  # repeat last
                        inc_arr[r] = 1

            if not inc_arr[r]:
                del data[r]

        return data

    def pisum(self, param_words, param_k, stat=1):
        '''
		情感值计算
		'''
        if not SentimentAnalysis.PNI:  # 负面评价词库
            SentimentAnalysis.PNI = self.getlines(SentimentAnalysis.DICTIONARY_DIR + 'PNi.txt')

        if not SentimentAnalysis.QNI:  # 负面情感词库
            SentimentAnalysis.QNI = self.getlines(SentimentAnalysis.DICTIONARY_DIR + 'QNi.txt')

        if not SentimentAnalysis.PPI:  # 正面评价词库
            SentimentAnalysis.PPI = self.getlines(SentimentAnalysis.DICTIONARY_DIR + 'PPi.txt')

        if not SentimentAnalysis.QPI:  # 正面情感词库
            SentimentAnalysis.QPI = self.getlines(SentimentAnalysis.DICTIONARY_DIR + 'QPi.txt')

        if not SentimentAnalysis.DEG:
            SentimentAnalysis.DEG = self.getfromini(SentimentAnalysis.DICTIONARY_DIR + 'deg.ini')  # 程度附词的系数

        if not SentimentAnalysis.COJ:
            SentimentAnalysis.COJ = self.getfromini(SentimentAnalysis.DICTIONARY_DIR + 'coj.ini')  # 关联词的系数

        if not SentimentAnalysis.SHIFT:
            SentimentAnalysis.SHIFT = self.getfromini(SentimentAnalysis.DICTIONARY_DIR + 'shift.ini')  # 转折词

        pni_dic = SentimentAnalysis.PNI
        qni_dic = SentimentAnalysis.QNI

        if stat == 1:  # 正面词库
            pi_dic = SentimentAnalysis.PPI
            qi_dic = SentimentAnalysis.QPI
        else:  # 负面词库
            pi_dic = SentimentAnalysis.PNI
            qi_dic = SentimentAnalysis.QNI

        deg_dic = SentimentAnalysis.DEG  # 程度附词的系数
        coj_dic = SentimentAnalysis.COJ  # 关联词的系数
        shift_dic = SentimentAnalysis.SHIFT  # 转折词

        # print '\r\n deg file:\r\n',deg_dic,'\r\n coj file:\r\n',coj_dic,'\r\n shift:\r\n',shift_dic, '\r\n'

        # file_data = self.getrelp(param_words, param_k)
        file_data = self.relateStmt(param_words, param_k)
        stat_val = dict()
        rec_arr = dict()
        deg_arr = dict()  # 算法记录组
        stat_v = dict()
        stat_k = 0
        # print u'\r\n这是 filedata\r\n',file_data,'\r\n';
        for stat_k in file_data.keys():
            stat_v = file_data[stat_k]
            stat_val[stat_k] = 0

            # 程度附词标记
            adv_num = 0  # 附词次数
            adj_num = 0  # 形容词次数
            verb_num = 0  # 情感次数
            d = 1  # 程度附词系数

            if stat_v.has_key('d'):
                for adv in stat_v['d']:
                    if adv[1] in pi_dic or adv[1] in qi_dic:
                        adv_num += 1
                        print '\r\n d detected,', adv, ' \r\n'
                    else:
                        continue

                    for adv1 in stat_v['d']:
                        if abs(adv[0] - adv1[0]) == 2 or abs(adv[0] - adv1[0]) == 1:
                            if not deg_arr.has_key(adv1[0]) and deg_dic.has_key(adv1[1]):  # adv1未被计算过
                                d *= float(deg_dic[adv1[1]])
                                deg_arr[adv1[0]] = 1
                                print '\r\n deg detected,', adv1[1], ' \r\n'

            if stat_v.has_key('a'):
                for adj in stat_v['a']:
                    if adj[1] in pi_dic or adj[1] in qi_dic:
                        adj_num += 1
                        print '\r\n a detected,', adj, ' \r\n'

                    if stat_v.has_key('d'):
                        for adv1 in stat_v['d']:
                            # print '\r\n d  d  adv1:\r\n', adv1, '\r\n', '\r\n j  j  adj:\r\n', adj, '\r\n'
                            if abs(adj[0] - adv1[0]) == 2 or abs(adj[0] - adv1[0]) == 1:

                                if (adv1[1] + adj[1]) in pni_dic or (adv1[1] + adj[1]) in qni_dic:
                                    if stat == 1:
                                        d *= -1
                                    else:
                                        adj_num += 1
                                    continue

                                # print '\r\n deg_arr \r\n', deg_arr, ' \r\n adv1 \r\n', adv1[1], '\r\n'
                                # print '\r\n deg_arr.has_key \r\n', deg_arr.has_key(adv1[0]), '\r\n deg_dic.has_key\r\n', deg_dic.has_key(adv1[1]),'\r\n'
                                if not deg_arr.has_key(adv1[0]) and deg_dic.has_key(adv1[1]):  # adv1未被计算过
                                    d *= float(deg_dic[adv1[1]])
                                    deg_arr[adv1[0]] = 1
                                    print '\r\n deg detected,', adv1[1], ' \r\n'

            if stat_v.has_key('v'):
                # print " 262 ：verb ", verb[1], " pi_dic " , pi_dic , "  qi_dic ", qi_dic, " \r\n"
                for verb in stat_v['v']:
                    if verb[1] in pi_dic or verb[1] in qi_dic:
                        verb_num += 1
                        print '\r\n v detected,', verb, ' \r\n'
                    else:
                        continue

                    if stat_v.has_key('d'):
                        for adv1 in stat_v['d']:
                            if abs(verb[0] - adv1[0]) == 2 or abs(verb[0] - adv1[0]) == 1:  # //在2个距离内的程度附词
                                if not deg_arr.has_key(adv1[0]) and deg_dic.has_key(adv1[1]):
                                    d *= float(deg_dic[adv1[1]])
                                    deg_arr[adv1[0]] = 1
                                    print '\r\n deg detected,', adv1[1], ' \r\n'

            if stat_val.has_key(stat_k):
                stat_val[stat_k] += (verb_num + adv_num + adj_num) * float(d)
                rec_arr[len(rec_arr)] = stat_val[stat_k]

            # 关联词标记
            # d = 1
            is_shift = False
            if stat_v.has_key('c'):

                for coj in stat_v['c']:

                    if coj_dic.has_key(coj[1]):
                        d *= coj_dic[coj[1]]

                    if coj[1] in shift_dic:
                        is_shift = True

            coj_ratio = 1
            if is_shift:
                coj_ratio = -2

            # 情感值为0时，取上句情感值的值，若是反面为-2
            if stat_val[stat_k] == 0:
                rec_arr[len(rec_arr)] = 'c'

                if stat_val.has_key(stat_k - 1) and stat_val[stat_k - 1] != 0:
                    stat_val[stat_k] = coj_ratio * stat_val[stat_k - 1]
                # continue
                elif stat_val.has_key(stat_k - 2) and stat_val[stat_k - 2] != 0:
                    stat_val[stat_k] = coj_ratio * stat_val[stat_k - 2]
                # continue
                elif stat_val.has_key(stat_k - 3) and stat_val[stat_k - 3] != 0:
                    stat_val[stat_k] = coj_ratio * stat_val[stat_k - 3]
                # continue
                elif stat_val.has_key(stat_k - 4) and stat_val[stat_k - 4] != 0:
                    stat_val[stat_k] = coj_ratio * stat_val[stat_k - 4]
                # continue
                elif stat_val.has_key(stat_k - 5) and stat_val[stat_k - 5] != 0:
                    stat_val[stat_k] = coj_ratio * stat_val[stat_k - 5]
                # continue
                else:
                    if is_shift:
                        stat_val[stat_k] = stat == 1 and -1 or 1
                    else:
                        stat_val[stat_k] = stat == 1 and 1 or -1
                # continue
                stat_val[stat_k] *= abs(float(d))

        for rk in range(len(rec_arr)):
            rv = rec_arr[rk]
            if rv == 'c':
                if rec_arr.has_key(rk - 1):
                    stat_val[rk] = 0
                elif rec_arr.has_key(rk - 2):
                    stat_val[rk] = 0
                elif rec_arr.has_key(rk + 1):
                    stat_val[rk] = 0
                elif rec_arr.has_key(rk + 2):
                    stat_val[rk] = 0
        print " stat_val ", stat_val, "\r\n"
        return stat_val

    def relateStmt(self, param_words=[], k=''):
        '''
		Replace the method of 'getrelp(param_words = [], k = ''):'
		'''
        word_arr = param_words
        line_split = ('.', '。', '……', '!', '?', '？', '！', '~')

        data = dict()
        class_arr = dict()
        stat_arr = dict()
        inc_arr = dict()

        order_arr = dict()
        coo_arr = list()

        si = 0

        for r in range(len(word_arr)):
            eArr = word_arr[r].strip().split('|')

            eArr[0] = int(eArr[0])
            eArr[3] = int(eArr[3])
            # print " si ", si,"\r\n"
            if not data.has_key(si):
                stat_arr[si] = u''
                data[si] = dict()
            if data[si].has_key(eArr[2]):
                data[si][eArr[2]].append([r, eArr[1]])
            else:
                data[si][eArr[2]] = [[r, eArr[1]]]

            if class_arr.has_key(si):
                class_arr[si].append(eArr[2])  # 词性
            else:
                class_arr[si] = [eArr[2]]  # 词性

            stat_arr[si] += eArr[1]  # 字符
            order_arr[eArr[0]] = si  # 索引->行号

            if eArr[2] == u'wp' and eArr[1] in line_split:

                if (len(stat_arr[si]) == 1):  # 该行只有结束符号

                    data.pop(si)
                    class_arr.pop(si)
                    stat_arr.pop(si)

                    order_arr.pop(eArr[0])
                    # print " continue wp","\r\n"
                    continue
                # print " si +=1 eArr ",eArr,"\r\n"
                si += 1

        headIndex = 0
        endIndex = 0
        # print " order_arr ", order_arr, "\r\n"
        for r in range(len(word_arr)):
            eArr = word_arr[r].strip().split('|')
            eArr[0] = int(eArr[0])
            eArr[3] = int(eArr[3])

            # print eArr," <-  eArr \r\n"
            if eArr[4] == u'COO':
                headIndex = order_arr[eArr[3]]
                endIndex = order_arr[eArr[0]]
                # print "eArr[3]  ", eArr[3], " eArr[0] ", eArr[0],"\r\n"
                if headIndex not in coo_arr:
                    coo_arr.append(headIndex)
                # print " COO append element ", coo_arr, "\r\n"

                if endIndex not in coo_arr:
                    coo_arr.append(endIndex)

        class_n = ('n', 'j', 'r', 'ni', 'nl', 'ns', 'nt', 'nz', 'nd', 'nh', 'ws')

        for r in range(len(class_arr)):  # r 行数
            c = class_arr[r]
            inc_arr[r] = 0  # 包含或不包含初始化

            if stat_arr[r].find(k) != -1:  # 显性包含关键字
                inc_arr[r] = 1

                cv = 0
                if r in coo_arr:
                    for ck in range(len(coo_arr)):
                        cv = coo_arr[ck]
                        inc_arr[cv] = 1

            if not inc_arr[r]:
                del data[r]

        # print coo_arr ," coo_arr ", "\r\n", " data ", data, "\r\n"
        return data

    def relateSentiment(self, param_words, param_k, stat=1):
        '''
		情感值计算 
		Replace method of 'pisum()'
		'''
        if not SentimentAnalysis.PNI:  # 负面评价词库
            SentimentAnalysis.PNI = self.getlines(SentimentAnalysis.DICTIONARY_DIR + 'PNi.txt')

        if not SentimentAnalysis.QNI:  # 负面情感词库
            SentimentAnalysis.QNI = self.getlines(SentimentAnalysis.DICTIONARY_DIR + 'QNi.txt')

        if not SentimentAnalysis.PPI:  # 正面评价词库
            SentimentAnalysis.PPI = self.getlines(SentimentAnalysis.DICTIONARY_DIR + 'PPi.txt')

        if not SentimentAnalysis.QPI:  # 正面情感词库
            SentimentAnalysis.QPI = self.getlines(SentimentAnalysis.DICTIONARY_DIR + 'QPi.txt')

        if not SentimentAnalysis.DEG:
            SentimentAnalysis.DEG = self.getfromini(SentimentAnalysis.DICTIONARY_DIR + 'deg.ini')  # 程度附词的系数

        if not SentimentAnalysis.COJ:
            SentimentAnalysis.COJ = self.getfromini(SentimentAnalysis.DICTIONARY_DIR + 'coj.ini')  # 关联词的系数

        if not SentimentAnalysis.SHIFT:
            SentimentAnalysis.SHIFT = self.getfromini(SentimentAnalysis.DICTIONARY_DIR + 'shift.ini')  # 转折词

        pni_dic = SentimentAnalysis.PNI
        qni_dic = SentimentAnalysis.QNI

        if stat == 1:  # 正面词库
            pi_dic = SentimentAnalysis.PPI
            qi_dic = SentimentAnalysis.QPI
        else:  # 负面词库
            pi_dic = SentimentAnalysis.PNI
            qi_dic = SentimentAnalysis.QNI

        deg_dic = SentimentAnalysis.DEG  # 程度附词的系数
        coj_dic = SentimentAnalysis.COJ  # 关联词的系数
        shift_dic = SentimentAnalysis.SHIFT  # 转折词

        # print '\r\n deg file:\r\n',deg_dic,'\r\n coj file:\r\n',coj_dic,'\r\n shift:\r\n',shift_dic, '\r\n'

        file_data = self.relateStmt(param_words, param_k)
        stat_val = dict()
        rec_arr = dict()
        deg_arr = dict()  # 算法记录组
        stat_v = dict()
        stat_k = 0
        # print u'\r\n这是 filedata\r\n',file_data,'\r\n';
        for stat_k in file_data.keys():
            stat_v = file_data[stat_k]
            stat_val[stat_k] = 0

            # 程度附词标记
            adv_num = 0  # 附词次数
            adj_num = 0  # 形容词次数
            verb_num = 0  # 情感次数

            if stat_v.has_key('d'):

                for adv in stat_v['d']:
                    adv_ev = 0  # 附词情感值

                    if adv[1] in pi_dic or adv[1] in qi_dic:
                        adv_ev = 1
                        print '\r\n d detected,', adv, ' \r\n'
                    else:
                        continue

                    for adv1 in stat_v['d']:
                        if abs(adv[0] - adv1[0]) == 2 or abs(adv[0] - adv1[0]) == 1:
                            if not deg_arr.has_key(adv1[0]) and deg_dic.has_key(adv1[1]):  # adv1未被计算过

                                # 排除转折词对结果影响，只计算单一面的情感，故continue
                                if float(deg_dic[adv1[1]]) < 0:
                                    continue

                                adv_ev *= float(deg_dic[adv1[1]])
                                deg_arr[adv1[0]] = 1
                                print '\r\n deg detected,', adv1[1], ' \r\n'

                    stat_val[stat_k] += adv_ev

            if stat_v.has_key('a'):

                for adj in stat_v['a']:
                    adj_ev = 0  # 形容词情感值

                    if adj[1] in pi_dic or adj[1] in qi_dic:
                        adj_ev = 1
                        print '\r\n a detected,', adj, ' \r\n'

                    if stat_v.has_key('d'):
                        for adv1 in stat_v['d']:
                            # print '\r\n d  d  adv1:\r\n', adv1, '\r\n', '\r\n j  j  adj:\r\n', adj, '\r\n'
                            if abs(adj[0] - adv1[0]) == 2 or abs(adj[0] - adv1[0]) == 1:

                                if (adv1[1] + adj[1]) in pni_dic or (adv1[1] + adj[1]) in qni_dic:
                                    if stat == 1:

                                        # 排除转折词对结果影响，只计算单一面的情感，故continue
                                        continue
                                    # adj_ev *= -1
                                    else:
                                        adj_ev += 1
                                    continue

                                # print '\r\n deg_arr \r\n', deg_arr, ' \r\n adv1 \r\n', adv1[1], '\r\n'
                                # print '\r\n deg_arr.has_key \r\n', deg_arr.has_key(adv1[0]), '\r\n deg_dic.has_key\r\n', deg_dic.has_key(adv1[1]),'\r\n'
                                if not deg_arr.has_key(adv1[0]) and deg_dic.has_key(adv1[1]):  # adv1未被计算过

                                    # 排除转折词对结果影响，只计算单一面的情感，故continue
                                    if float(deg_dic[adv1[1]]) < 0:
                                        continue

                                    adj_ev *= float(deg_dic[adv1[1]])
                                    deg_arr[adv1[0]] = 1
                                    print '\r\n deg detected,', adv1[1], ' \r\n'

                    stat_val[stat_k] += adj_ev

            if stat_v.has_key('v'):

                for verb in stat_v['v']:
                    verb_ev = 0  # 动词情感值

                    if verb[1] in pi_dic or verb[1] in qi_dic:
                        verb_ev = 1
                        print '\r\n v detected,', verb, ' \r\n'
                    else:
                        continue

                    if stat_v.has_key('d'):
                        for adv1 in stat_v['d']:
                            if abs(verb[0] - adv1[0]) == 2 or abs(verb[0] - adv1[0]) == 1:  # //在2个距离内的程度附词
                                if not deg_arr.has_key(adv1[0]) and deg_dic.has_key(adv1[1]):

                                    # 排除转折词对结果影响，只计算单一面的情感，故continue
                                    if float(deg_dic[adv1[1]]) < 0:
                                        continue

                                    verb_ev *= float(deg_dic[adv1[1]])
                                    deg_arr[adv1[0]] = 1
                                    print '\r\n deg detected,', adv1[1], ' \r\n'

                    stat_val[stat_k] += verb_ev

            if stat_val.has_key(stat_k):
                # stat_val[stat_k] += (verb_num + adv_num + adj_num) * float(d)
                rec_arr[len(rec_arr)] = stat_val[stat_k]

            """
			#关联词标记
			is_shift = False
			if stat_v.has_key('c'):

				for coj in stat_v['c']:

					if coj[1] in shift_dic:
						is_shift = True

			coj_ratio = 1

			if is_shift:
				coj_ratio = -2
				#排除转折词的影响，只计算单方面情感值,故continue
				continue

			#情感值为0时，取上句情感值的值，若是反面为-2
			if stat_val[stat_k] == 0:
				rec_arr[len(rec_arr)] = 'c'

				if stat_val.has_key(stat_k - 1) and stat_val[stat_k - 1] != 0:
					stat_val[stat_k] = coj_ratio * stat_val[stat_k - 1]
				
				elif stat_val.has_key(stat_k - 2) and stat_val[stat_k - 2] != 0:
					stat_val[stat_k] = coj_ratio * stat_val[stat_k - 2]
				
				elif stat_val.has_key(stat_k - 3) and stat_val[stat_k - 3] != 0:
					stat_val[stat_k] = coj_ratio * stat_val[stat_k - 3]
				
				elif stat_val.has_key(stat_k - 4) and stat_val[stat_k - 4] != 0:
					stat_val[stat_k] = coj_ratio * stat_val[stat_k - 4]
				
				elif stat_val.has_key(stat_k - 5) and stat_val[stat_k - 5] != 0:
					stat_val[stat_k] = coj_ratio * stat_val[stat_k - 5]
				
				else:
					if is_shift:
						stat_val[stat_k] = stat == 1 and -1 or 1
					else:
						stat_val[stat_k] = stat == 1 and 1 or -1
			"""

        '''
		for rk in range(len(rec_arr)):
			rv = rec_arr[rk]
			if rv == 'c':
				if rec_arr.has_key(rk-1):
					stat_val[rk] = 0
				elif rec_arr.has_key(rk-2):
					stat_val[rk] = 0
				elif rec_arr.has_key(rk+1):
					stat_val[rk] = 0
				elif rec_arr.has_key(rk+2):
					stat_val[rk] = 0
		'''
        print " stat_val ", stat_val, "\r\n"
        return stat_val
