import requests as rq
from bs4 import BeautifulSoup
import re
import time
import random
import pandas as pd


def crawler_104(jobname, page):
    for _page in range(1, page):
        web_104 = rq.get('https://www.104.com.tw/jobs/search/?ro=0&keyword='+jobname+'&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&order=1&asc=0&page='+str(_page)+'&mode=s&jobsource=2018indexpoc',
                         headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)'
                              ' Chrome/52.0.2743.116 Safari/537.36'})

        soup = BeautifulSoup(web_104.text, 'lxml')
        df = pd.DataFrame(columns=['job_name', 'company', 'date', 'web', 'workExp', 'region', 'salary',
                                   'jobCategory', 'specialty', 'jobDescription', 'condition', 'welfare'])
        for i in range(1, 21):
            web = 'https:' + soup.find_all('article')[i].find_all('a')[0]['href']
            web_company = re.findall('job/(.*?)\?',web)[0]
            rt = rq.get('https://www.104.com.tw/job/ajax/content/'+web_company,
                        headers={'Referer': 'https://www.104.com.tw/job/750o4?jobsource=jolist_a_relevance'})

            content = rt.json()
            df = df.append({'job_name': content['data']['header']['jobName'],
                            'company': content['data']['header']['custName'],
                            'date': content['data']['header']['appearDate'],
                            'web': web,
                            'workExp':content['data']['condition']['workExp'],
                            'region':content['data']['jobDetail']['addressRegion'],
                            'salary': content['data']['jobDetail']['salary'],
                            'jobCategory': [x['description'] for x in content['data']['jobDetail']['jobCategory']],
                            'specialty': [x['description'] for x in content['data']['condition']['specialty']],
                            'jobDescription': content['data']['jobDetail']['jobDescription'],
                            'condition': content['data']['condition']['other'],
                            'welfare': content['data']['welfare']['welfare']
                            }, ignore_index=True)
            time.sleep(random.uniform(0, 2))  # 友善爬蟲
    return df

