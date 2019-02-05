import pandas as pd
import requests
from tqdm import tqdm_notebook as tqdm
import lxml
from lxml import html
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import os as os



os.environ['http_proxy'] = 'http://proxy.ifmo.ru:3128'

# df = pd.read_csv("big5_users.tsv", sep='\t')
df = pd.read_excel("big5_main.xlsx")
print("len:", len(df))
df['gender'] = df['gender'].apply(lambda x: x == "м")

def big5_profile(target):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(target, headers=headers)
    tree = html.fromstring(response.content) # convert content text to lxml obj
    target_element_list = tree.xpath(r".//div[@class='stdTbl']/table/tr")
    factors = []
    score_dict = {}
    for tr in target_element_list:
        td_list = []
        isfactor = False
        for td in tr:
            if td.get("class") == "jFL jBF":
                factors.append(tr)
                isfactor = True
                break
            td_list.append(td.text)
        
        if not isfactor and td_list[0] and td_list[0].isalpha() and not td_list[0].isdigit():
            scores = [x for x in td_list if x != '\xa0']
            score = scores[1]
            subfactor_name = "{}__{}".format(td_list[0], td_list[-1]).replace(" ", "_")
            score_dict.update({
                subfactor_name: score
            })
    
    for tr in factors:
        td_scores = [e for e in list(tr) if e.text != '\xa0']
        td_score = [x.text for x in td_scores if x.text][0]
        factor_name = "#{}_{}".format(td_list[0].find("a").text, td_list[-1].find("a").text)
        score_dict.update({factor_name: td_score})
    return score_dict

def big5_profile_adv(target):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(target, headers=headers)
    tree = html.fromstring(response.content) # convert content text to lxml obj
    target_element_list = tree.xpath(r".//div[@class='stdTbl']/table/tr")
    
    score_dict = {}
    for tr in target_element_list:
        td_first = tr.find("td")
        td_list = list(tr)
        if td_first.get("class") == "jFL jBF":
            td_scores = [e for e in td_list if e.text != '\xa0']
            td_score = [x.text for x in td_scores if x.text][0]
            factor_name = "#{}_{}".format(td_list[0].find("a").text, td_list[-1].find("a").text)
            score_dict.update({factor_name: td_score})
            
        if td_first.get("class") == "jFL":
            td_scores = [e for e in td_list if e.text != '\xa0']
            td_score = [x.text for x in td_scores if x.text][1]
            factor_name = "{}__{}".format(td_list[0].text, td_list[-1].text)
            score_dict.update({factor_name: td_score})
            
    return score_dict

total_scores_list = []
for owner_id, big5_link, friends, gender in tqdm(zip(df['owner_id'].values, df['big5'].values, df['friends'].values, df['gender'].values)):
    print(owner_id, big5_link)
    ofile_path = "data/{}.html".format(owner_id)
    score_dict = big5_profile_adv(big5_link)
    score_dict["###owner_id"] = owner_id
    score_dict["##friends"] = friends
    score_dict["##gender"] = gender
    total_scores_list.append(score_dict)

df_stats = pd.DataFrame.from_records(total_scores_list)

print("cols:", df_stats.columns.__len__())

for c in df_stats.columns:
    if c != "##gender":
        df_stats[c] = df_stats[c].astype(float)
new_headers = ['owner_id','friends','gender','sCON','sEXT','sAGR','sOPN','sNEU']
df_stats = df_stats[['###owner_id','##friends','##gender','#импульсивность_самоконтроль','#интроверсия_экстраверсия','#обособленность_привязанность','#практичность_экспрессивность','#эмоц. устойчивость_эмоц. неустойчивость']]
df_stats.to_csv("big5_stats.tsv", index=False, sep='\t', encoding='utf-8', header = new_headers)



