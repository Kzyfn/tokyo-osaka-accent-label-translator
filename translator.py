import pyopenjtalk
import numpy as np
import pandas as pd



def create_osaka_accent_labels_from_text(text):
    keitaiso, fullcontext_label = pyopenjtalk.run_frontend(text)
    
    accent_labels = []
    prev_accent_type = 0
    
    for tmp_keitaiso in keitaiso:
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
                osaka_accent_label_tmp, post_accent_type = translate_accent_noun(accent_type, tokyo_accent_label_tmp, mora_num)
            elif (tmp_keitaiso[1] == '動詞' and tmp_keitaiso[2] == '自立') or (tmp_keitaiso[1] == '動詞' and tmp_keitaiso[2] == '接尾' and tmp_keitaiso[7] == 'ある'):
                osaka_accent_label_tmp, post_accent_type = translate_accent_verb(accent_type, tokyo_accent_label_tmp, mora_num, tmp_keitaiso)
            elif tmp_keitaiso[1] == '形容詞':
                osaka_accent_label_tmp, post_accent_type = translate_accent_adjective(accent_type, tokyo_accent_label_tmp, mora_num, tmp_keitaiso)
            elif tmp_keitaiso[1] == '助詞':
                osaka_accent_label_tmp, post_accent_type = translate_accent_joshi(tmp_keitaiso, tokyo_accent_label_tmp, prev_accent_type)
            elif tmp_keitaiso[1] == '助動詞' or (tmp_keitaiso[1] == '動詞' and tmp_keitaiso[2] == '接尾'):
                osaka_accent_label_tmp, post_accent_type = translate_accent_jodoushi(tmp_keitaiso, tokyo_accent_label_tmp, prev_accent_type)
            else:
                osaka_accent_label_tmp = tokyo_accent_label_tmp
                
            accent_labels+= list(osaka_accent_label_tmp)
            prev_accent_type = post_accent_type
            
    return accent_labels




def translate_accent_noun(f2, tokyo_hl_label, mora_num):
    """
    f2 はアクセント型
    """
    if f2 != 1:
        if mora_num == 2 and f2 == 2:
            tokyo_hl_label[0] = 1
            tokyo_hl_label[1] = 0
        else:
            tokyo_hl_label[0] = 1
            if f2 == 0:
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
    
    
def translate_accent_verb(f2, tokyo_hl_label, mora_num, keitaiso):
    basic_form = keitaiso[7]
    katsuyougata = keitaiso[5]
    katsuyoukei = keitaiso[6]
    
    accent_type = int(pyopenjtalk.run_frontend(basic_form)[0][0].split(',')[-3].split('/')[0])
    
    if accent_type == 0 or '五段' in katsuyougata: #とりあえず全部H0型にする
        osaka_accent_label = np.ones(mora_num)
        
        if '仮定' in katsuyougata or '命令' in katsuyougata:
            osaka_accent_label[-1] = 0
        
        if '連用' in katsuyougata or '未然' in katsuyougata:
            post_hl = 1
        else:
            post_hl = 0

        if '連用タ接続' in katsuyoukei:# ~~ た
            osaka_accent_label = np.zeros(mora_num)
            osaka_accent_label[0] = 1
            post_hl = 0
        
    elif 'カ変' in katsuyougata:
        if '未然' in katsuyoukei or '連用' in katsuyoukei:
            osaka_accent_label = np.ones(mora_num)
        elif '基本' in katsuyoukei or '仮定' in katsuyoukei:
            osaka_accent_label = np.zeros(mora_num)
            osaka_accent_label[-1] = 1
        else:
            osaka_accent_label = tokyo_hl_label
            
        if ('連用' in katsuyougata or '未然' in katsuyougata) and '連用タ接続' not in katsuyoukei:
            post_hl = 1
        else:
            post_hl = 0

    elif 'サ変' in katsuyougata:
        if '仮定' in katsuyoukei or '命令' in katsuyoukei:
            osaka_accent_label = np.ones(mora_num)
            osaka_accent_label[-1] = 0
        else:
            osaka_accent_label = np.ones(mora_num)
            
        if ('連用' in katsuyougata or '未然' in katsuyougata) and '連用タ接続' not in katsuyoukei:
            post_hl = 1
        else:
            post_hl = 0
    
    
    else:
        osaka_accent_label = np.zeros(mora_num)
        post_hl = 0
        
        if ( '未然' in katsuyoukei or '基本' in katsuyoukei ) and '未然ウ接続' not in katsuyougata:
            osaka_accent_label[-1] = 1
        elif '仮定' in katsuyoukei or '命令' in katsuyoukei:
            if mora_num == 1:
                osaka_accent_label = tokyo_hl_label
            else:
                osaka_accent_label[-2] = 1
        elif '未然ウ接続' not in katsuyougata:
            osaka_accent_label = np.zeros(mora_num)
            post_hl = 1
        else:
            osaka_accent_label = np.zeros(mora_num)
        
        if mora_num == 1 and '連用' in katsuyougata:
            osaka_accent_label = np.ones(1)
            post_hl = 1
        
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
            
    elif 'ガル接続' in katsuyoukei:
        osaka_label = np.ones(mora_num)
        post_hl = 1
        
    elif '連用' in katsuyoukei:
        osaka_label = np.ones(mora_num)
        osaka_label[-2:] = 0
        
    elif '基本' in katsuyoukei or '連体' in katsuyoukei or '仮定' in katsuyoukei:
        osaka_label = np.ones(mora_num)
        osaka_label[-2:] = 0
    else:
        assert False, f"知らない活用形です: 形容詞: {katsuyoukei}"
    
    return osaka_label, post_hl


def translate_accent_joshi(keitaiso, tokyo_hl, prev_hl):
    joshi_class = keitaiso[2]
    text = keitaiso[0]

    
    table = pd.read_csv('data/joshi_accent_translation_table.csv')
    row = table[(table['単語'] == text) & (table['助詞種類'] == joshi_class)]
    
    
    if row.shape[0] == 0:
        print(f"辞書がありません．東京方言アクセントラベルを返します．{joshi_class}: {text}")
        return tokyo_hl, prev_hl
    
    osaka_label = row['大阪弁アクセント'].values[0].replace('L', str(0)).replace('H', str(1)).replace('*', str(prev_hl)).split()
    osaka_label = [int(x) for x in osaka_label]

    
    return osaka_label, prev_hl


def translate_accent_jodoushi(keitaiso, tokyo_hl, prev_hl):
    base_form = keitaiso[7]
    text = keitaiso[0]
    katsuyoukei = keitaiso[6] if '基本' not in keitaiso[6] else '終止'
    
    try:
        hl_table = pd.read_csv(f'./data/jodoushi_hl_tables/{base_form}.csv')
    except:
        print(f"辞書がありません．東京方言アクセントラベルを返します．助動詞: {text}")
        return tokyo_hl, tokyo_hl[-1]
    
    for col, row in hl_table.iterrows():
        if katsuyoukei in  row['活用形'] and text in row['活用形']:
            osaka_hl_labels = row['アクセントラベル'].replace('*', str(prev_hl)).replace('H', str(1)).replace('L', str(0)).split()
            osaka_hl_labels = [int(x) for x in osaka_hl_labels]
            
            return osaka_hl_labels, prev_hl
        

    print(keitaiso)
    print(hl_table, katsuyoukei, text)
    assert False, f'知らない活用形です．助動詞 {base_form} の {katsuyoukei}: {text}'
    return tokyo_hl


import sys


if __name__ == '__main__':
    args = sys.argv
    print(args[1])
    hl_labels = create_osaka_accent_labels_from_text(args[1])
    print(hl_labels)