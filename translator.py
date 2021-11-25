import pyopenjtalk
import numpy as np
import pandas as pd

def is_followed_by_ta(keitaiso):
    return ((keitaiso[7] == 'た' and keitaiso[1] == '助動詞') or (keitaiso[0] == 'て' and keitaiso[1] == '助詞'))

def is_followed_by_souda_youda(keitaiso):
    return ((keitaiso[7] == 'そう' and keitaiso[1] == '名詞' and keitaiso[3] ==  '助動詞語幹') or (keitaiso[0] == 'よう' and keitaiso[1] == '名詞' and keitaiso[3] ==  '助動詞語幹'))

def is_followed_by_reru_seru(keitaiso):
    is_sub_verb = keitaiso[1] == '動詞' and keitaiso[2] == '接尾'
    return ((keitaiso[7] == 'せる' or keitaiso[7] == 'させる' or keitaiso[7] == 'れる' or keitaiso[7] == 'られる') and is_sub_verb)

def create_osaka_accent_labels_from_text(text):
    keitaiso, fullcontext_label = pyopenjtalk.run_frontend(text)
    
    accent_labels = []
    prev_accent_type = 0
    
    for k, tmp_keitaiso in enumerate(keitaiso):
        tmp_keitaiso = tmp_keitaiso.split(',')
        if tmp_keitaiso[1] in ['記号', 'フィラー']:
            continue
        else:
            # モーラが存在する場合            
            accent_type, mora_num = map(int, tmp_keitaiso[-3].split('/'))
            
            if mora_num == 0:
                print(tmp_keitaiso)
            
            if accent_type == 0:
                tokyo_accent_label_tmp = np.ones(mora_num)
                tokyo_accent_label_tmp[0] = 0
            elif accent_type == 1:
                tokyo_accent_label_tmp = np.zeros(mora_num)
                tokyo_accent_label_tmp[0] = 1
            else:
                tokyo_accent_label_tmp = np.ones(mora_num)
                tokyo_accent_label_tmp[0] = 0
                tokyo_accent_label_tmp[accent_type:] = 0
                
            
            if tmp_keitaiso[1] in ['名詞', '副詞']:
                if '助動詞語幹' in tmp_keitaiso[3]:
                    osaka_accent_label_tmp, post_accent_type = translate_accent_noun_jodoushi(tmp_keitaiso)
                else:
                    osaka_accent_label_tmp, post_accent_type = translate_accent_noun(accent_type, tokyo_accent_label_tmp, mora_num, text=tmp_keitaiso[0])
            elif (tmp_keitaiso[1] == '動詞' and tmp_keitaiso[2] == '自立') or (tmp_keitaiso[1] == '動詞' and tmp_keitaiso[2] == '接尾' and tmp_keitaiso[7] == 'ある'):
                noun_followed = False if len(keitaiso) - 1 <= k else  keitaiso[k+1].split(',')[1] == '名詞'
                ta_followed = False if len(keitaiso) - 1 <= k else  is_followed_by_ta(keitaiso[k+1].split(',')) # l0 型動詞の音便なしの連用形のアクセントのために必要．
                seru_reru_followed = False if len(keitaiso) - 1 <= k else  is_followed_by_reru_seru(keitaiso[k+1].split(',')) # l0 型動詞の音便なしの連用形のアクセントのために必要．
                sou_you_followed = False if len(keitaiso) - 1 <= k else is_followed_by_souda_youda(keitaiso[k+1].split(','))
                
                osaka_accent_label_tmp, post_accent_type = translate_accent_verb(accent_type, tokyo_accent_label_tmp, mora_num, tmp_keitaiso, 
                                                                                 noun_followed=noun_followed, ta_followed=ta_followed, seru_reru_followed=seru_reru_followed, sou_you_followed=sou_you_followed)
                
            elif tmp_keitaiso[1] == '形容詞':
                osaka_accent_label_tmp, post_accent_type = translate_accent_adjective(accent_type, tokyo_accent_label_tmp, mora_num, tmp_keitaiso)
            elif tmp_keitaiso[1] == '助詞':
                osaka_accent_label_tmp, post_accent_type = translate_accent_joshi(tmp_keitaiso, tokyo_accent_label_tmp, prev_accent_type)
            elif tmp_keitaiso[1] == '助動詞' or (tmp_keitaiso[1] == '動詞' and tmp_keitaiso[2] == '接尾'):
                ta_followed = False if len(keitaiso) - 1 <= k else  is_followed_by_ta(keitaiso[k+1].split(',')) # l0 型動詞の音便なしの連用形のアクセントのために必要．
                
                osaka_accent_label_tmp, post_accent_type = translate_accent_jodoushi(tmp_keitaiso, tokyo_accent_label_tmp, prev_accent_type, mora_num, ta_followed=ta_followed)
            else:
                osaka_accent_label_tmp = tokyo_accent_label_tmp
                post_accent_type = 1
                
            accent_labels+= list(osaka_accent_label_tmp)
            prev_accent_type = post_accent_type
            
    return accent_labels


def translate_accent_noun_jodoushi(keitaiso):
    if keitaiso[0] in ['そう', 'よう']:
        return [1. , 0.], 0
    elif keitaiso[0] in ['そ', 'よ']:# これは仕方なし，本当はやりたくない
        return [1. ], 0
    else:
        assert False, '知らない助動詞語幹です'

def translate_accent_noun(f2, tokyo_hl_label, mora_num, text=None):
    """
    f2 はアクセント型
    """
    
    if text == 'とき' or text == '時':
        return np.array([1, 0]), 0
    
    if f2 != 1:
        if mora_num == 2 and f2 == 2:
            tokyo_hl_label[0] = 1
            tokyo_hl_label[1] = 0
        else:
            tokyo_hl_label[0] = 1
            if f2 == 0 or f2 > mora_num:
                return tokyo_hl_label, 1
        return tokyo_hl_label, 0
    
    elif mora_num == 2:
        tokyo_hl_label[0] = 0
        tokyo_hl_label[1] = 1
        return tokyo_hl_label, 0
    
    elif mora_num == 1:
        tokyo_hl_label[0] = 1
        return tokyo_hl_label, 0
    else: #3モーラ以上の名詞 * 1型アクセントは東京都大阪で共通
        return tokyo_hl_label, 0
    
    
def translate_accent_verb(f2, tokyo_hl_label, mora_num, keitaiso, noun_followed=False, ta_followed=False, seru_reru_followed=False, sou_you_followed=False):
    basic_form = keitaiso[7]
    katsuyougata = keitaiso[5]
    katsuyoukei = keitaiso[6]
    
    accent_nucleus_tmp = int(keitaiso[-3].split('/')[0])
    accent_type, base_form_mora_num = map(int, pyopenjtalk.run_frontend(basic_form)[0][0].split(',')[-3].split('/'))
    
    if accent_type == 0 or '五段' in katsuyougata: #とりあえず五段と無核は全部H0型にする
        osaka_accent_label = np.ones(mora_num)
        
        if '仮定' in katsuyoukei or '命令' in katsuyoukei:
            osaka_accent_label[-1] = 0
        
        if '連用' in katsuyoukei or '未然' in katsuyoukei:
            post_hl = 1
        else:
            post_hl = 0

        if '連用タ接続' in katsuyoukei or ('連用' in katsuyoukei and ta_followed): # 音便がある組とない組
            if base_form_mora_num in [2, 3]:#散る，走る，揚げる，いる，消す，移す
                osaka_accent_label = np.zeros(mora_num)
                osaka_accent_label[0] = 1
                post_hl = 0
            else: # 飛び上がる
                if '促音便' in keitaiso[5]:
                    osaka_accent_label = np.ones(mora_num)
                    osaka_accent_label[-2:] = 0
                    post_hl = 0
                else:#呼びだす，打ち上げる，
                    osaka_accent_label = np.ones(mora_num)
                    osaka_accent_label[-1] = 0
                    post_hl = 0
        
    elif 'カ変' in katsuyougata:
        if '未然' in katsuyoukei or '連用' in katsuyoukei:
            osaka_accent_label = np.ones(mora_num)
        elif '基本' in katsuyoukei or '仮定' in katsuyoukei:
            osaka_accent_label = np.zeros(mora_num)
            osaka_accent_label[-1] = 1
        elif '連体' in katsuyoukei:
            osaka_accent_label = np.zeros(mora_num)
        else:
            osaka_accent_label = tokyo_hl_label
            
        if ('連用' in katsuyoukei or '未然' in katsuyoukei) and '連用タ接続' not in katsuyoukei:
            post_hl = 1
        else:
            post_hl = 0

    elif 'サ変' in katsuyougata:
        if '仮定' in katsuyoukei or '命令' in katsuyoukei:
            osaka_accent_label = np.ones(mora_num)
            osaka_accent_label[-1] = 0
        else:
            osaka_accent_label = np.ones(mora_num)
            
        if ('連用' in katsuyoukei or '未然' in katsuyoukei) and '連用タ接続' not in katsuyoukei:
            post_hl = 1
        else:
            post_hl = 0
    
    
    else:
        # 五段でない and 東京方言でアクセント核をもつ
        osaka_accent_label = np.zeros(mora_num)
        post_hl = 0
        
        if ( '未然' in katsuyoukei or '基本' in katsuyoukei ) and '未然ウ接続' not in katsuyoukei:
            if noun_followed:# 連体形
                osaka_accent_label = np.zeros(mora_num)
                post_hl = 1
            elif seru_reru_followed:# れるられる，せるさせる接続
                osaka_accent_label = np.zeros(mora_num)
            else:
                 osaka_accent_label[-1] = 1
                    
        elif '仮定' in katsuyoukei or '命令' in katsuyoukei:
            if mora_num == 1:
                osaka_accent_label = tokyo_hl_label
            if mora_num == 2:
                osaka_accent_label[-1] = 1
            else:
                osaka_accent_label[-2] = 1
                
        elif '未然ウ接続' not in katsuyoukei:#連用形
            if base_form_mora_num == 2: # 見る
                osaka_accent_label = np.ones(mora_num)
                post_hl = 1
                    
            elif base_form_mora_num == 3: # 受ける，
                if accent_nucleus_tmp > mora_num or sou_you_followed:# ます接続
                    osaka_accent_label = np.zeros(mora_num)
                else:
                    osaka_accent_label = np.zeros(mora_num)
                    osaka_accent_label[-1] = 1
            else:
                if accent_nucleus_tmp > mora_num or sou_you_followed:# ます接続
                    osaka_accent_label = np.zeros(mora_num)
                else:
                    osaka_accent_label = np.zeros(mora_num)
                    osaka_accent_label[-2] = 1
        
            
        else:
            """
            なぜか助動詞「よう」の「よ」は動詞の一部としてみなされるようなので，openjtalkに合わせて修正
            調べよう => ['調べよ,動詞,自立,*,*,一段,未然ウ接続,調べる,シラベヨ,シラベヨ,3/4,*,-1', 'う,助動詞,*,*,*,不変化型,基本形,う,ウ,ー,0/1,動詞%F1/特殊助動詞%F2@0,1']
            """
            osaka_accent_label = np.zeros(mora_num)
            osaka_accent_label[-1] = 1
            post_hl = 1
        
        if mora_num == 1 and '連用' in katsuyoukei:
            osaka_accent_label = np.ones(1)
            post_hl = 0
        
    return osaka_accent_label, post_hl


def translate_accent_adjective(f2, tokyo_hl_label, mora_num, keitaiso):
    katsuyoukei = keitaiso[6]
    phonemes = pyopenjtalk.g2p(keitaiso[-4])
    post_hl = 0
    
    if '未然' in katsuyoukei:
        karou = phonemes[-1] in ['O', 'o']
        if karou:#かろ〜〜，なら
            osaka_label = np.ones(mora_num)
        else:#~~くない，なら
            osaka_label = np.ones(mora_num)
            osaka_label[-1] = 0
            
    elif '連用タ接続' in katsuyoukei:
        osaka_label = np.ones(mora_num)
        osaka_label[-2:] = 0
    elif '連用' in katsuyoukei:
        osaka_label = np.ones(mora_num)
        osaka_label[-1] = 0
    elif 'ガル接続' in katsuyoukei:
        osaka_label = np.ones(mora_num)
        post_hl = 1
        
    elif '基本' in katsuyoukei or '連体' in katsuyoukei or '仮定' in katsuyoukei:
        osaka_label = np.ones(mora_num)
        osaka_label[-2:] = 0
    else:
        assert False, f"知らない活用形です: {katsuyoukei}"
    
    return osaka_label, post_hl


def translate_accent_joshi(keitaiso, tokyo_hl, prev_hl):
    joshi_class = keitaiso[2]
    text = keitaiso[0]
    
    table = pd.read_csv('data/joshi_accent_translation_table.csv')
    row = table[table['単語'] == text][table['助詞種類'] == joshi_class]

    
    if row.shape[0] == 0:
        return tokyo_hl, prev_hl
    
    osaka_label = row['大阪弁アクセント'].values[0].replace('L', str(0)).replace('H', str(1)).replace('*', str(prev_hl)).split()
    osaka_label = [int(x) for x in osaka_label]

    
    return osaka_label, prev_hl


def translate_accent_jodoushi(keitaiso, tokyo_hl, prev_hl, mora_num, ta_followed=False):
    base_form = keitaiso[7]
    text = keitaiso[0]
    

    if ta_followed and '連用' in keitaiso[6]:
        osaka_hl_labels = np.zeros(mora_num)
        prev_hl = 0
        if mora_num > 1:
            osaka_hl_labels = np.zeros(mora_num)
            osaka_hl_labels[0] = 1
        return osaka_hl_labels, prev_hl

    for tmp_katsuyoukei in ['未然', '連用',  '連用タ接続', '基本', '連体', '仮定', '命令', 'ガル接続', '体言接続']:
        if tmp_katsuyoukei in keitaiso[6]:
            katsuyoukei = tmp_katsuyoukei if '基本' not in keitaiso[6] else '終止'
            break
        
            
    try:
        katsuyoukei
    except:
        print('助動詞，知らない活用形です．')
        print(base_form)
        print(keitaiso, keitaiso[6])
    
        
    
    try:
        hl_table = pd.read_csv(f'./data/jodoushi_hl_tables/{base_form}.csv')
    except:
        #print('jodoushi_hl_tables に該当アクセントがありません，東京方言アクセントを返します')
        #print(base_form)
        return tokyo_hl, prev_hl
    
    for col, row in hl_table.iterrows():
        if katsuyoukei in  row['活用形'] and text in row['活用形']:
            osaka_hl_labels = row['アクセントラベル'].replace('*', str(prev_hl)).replace('H', str(1)).replace('L', str(0)).split()
            osaka_hl_labels = [int(x) for x in osaka_hl_labels]

            return osaka_hl_labels, prev_hl
    
    print('助動詞アクセントファイルに不足があります．')
    print(f'終止形: {base_form}, 活用形: {keitaiso}')
    #assert False, '失敗'
    return tokyo_hl, prev_hl
    
    