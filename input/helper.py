
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('ggplot')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['figure.facecolor']='w'
plt.rcParams['savefig.facecolor']='w'
plt.rcParams['text.color']='b'
plt.rcParams['xtick.labelsize']=16
plt.rcParams['ytick.labelsize']=16

import pandas as pd

from collections import namedtuple
CalFunc=namedtuple('CalFunc','col func name')
Report_msg=namedtuple('Report_msg','df axes sheet_name')


def desc_ays_columns_msgs(x_df):
    '''
    列信息
    '''
    # 每列缺失值
    df_na=x_df.isna().sum()
    df_na.name='缺失值'
    # 每列的数据类型
    df_types=x_df.dtypes
    df_types.name='列类型'
    # 放入 DataFrame
    df_tmp=pd.DataFrame([df_na,df_types])
    # 统计描述
    df_des=x_df.describe(include='all')
    # 合并表
    tmp=pd.concat([df_des,df_tmp])
    return tmp,'describe'

def desc_ays_na_rows(x_df):
    '''
    缺失值记录
    '''
    cond= x_df.isna().any(axis=1)
    res=x_df[cond]
    return res,'缺失值记录'

def desc_ays_corr(x_df):
    '''
    相关性
    '''
    return x_df.corr(),'corr'

g_default_methods=[
    desc_ays_columns_msgs,
    desc_ays_na_rows,
    desc_ays_corr
    ]


def create_desc_ays(x_df,methods=None,file_name='desc_ays.xlsx'):
    '''
    创建统计描述
    '''
    # 默认方法 + 外部传入的方法
    if methods:
        methods=g_default_methods+methods
    else:
        methods=g_default_methods.copy()
    # 每个方法执行，并输出到excel的工作表上
    with pd.ExcelWriter(file_name) as ew:
        for m in methods:
            res,wrk_name=m(x_df)
            res.to_excel(ew,wrk_name)
        ew.save()


def cal(df , keys , *cal_funcs):
    '''
    cal_funcs : 返回值必须是 namedtuple('CalFunc','col func name')
        比如：helper.CalFunc(col='销售数量',func='sum',name='总销量')
    '''
    # 把传入的每个统计方法，转为字典
    funcs=(f() for f in cal_funcs)
    agg_dicts={
        v.name : (v.col,v.func)
        for v in funcs
    }
    # 汇总
    res=(
        df.groupby(keys)
            .agg(**agg_dicts)
    )

    return res

def df_top_n(x_df,col,n,by=None):
    '''
    求 top n
    col：数值列
    n：top n
    by：按某个组求 top n
    '''
    if by:
        res= x_df.groupby(by,as_index=False).apply(
            lambda x:x.nlargest(n,col)
        )
        return res.reset_index(0,drop=True)
    return x_df.nlargest(n,col)

def export_excel(report_msgs,file_name='anl_report.xlsx'):
    with pd.ExcelWriter(file_name) as ew:
        for r in report_msgs:
            df,ax,wrk_name=r.df,r.axes,r.sheet_name

            imgdata = BytesIO()
            fig=ax.get_figure()
            fig.patch.set_alpha(0.3)
            # ax.tick_params(labelsize=16)
            fig.savefig(imgdata, format="png")
            imgdata.seek(0)

            df.to_excel(ew,wrk_name)
            wrk=ew.sheets[wrk_name]
            cols = len(df.columns) + df.index.nlevels + 1
            wrk.insert_image(
                1, cols, "",
                {'image_data': imgdata}
            )

        ew.save()