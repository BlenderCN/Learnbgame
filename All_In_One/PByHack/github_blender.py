# coding: utf-8
import time
import json
import requests
from git import Repo
#from db import REDIS
import os
REPO_SHOW = '1'
REPO_HIDDEN = '0'

SEARCH_API = 'https://api.github.com/search/repositories?q=%s&type=Code&sort=updated&order=desc&page=%s'

def download_dataset(dataset_url):
    local_git = './Download/'+dataset_url.split('/')[4]
    if not os.path.exists(local_git):
        repo = Repo.clone_from(url=dataset_url+'.git', to_path=local_git)
        print("Downloaded")
    else:
        print("Repo exists, pulling latest")
        repo = Repo(local_git)
        git = repo.git
        git.checkout("master")
        repo.remotes[0].pull()
    return repo

def search_github(keyword):
    # 爬取 20 页最新的列表
    for i in range(1, 21):
        res = requests.get(SEARCH_API % (keyword, i))
        repo_list = res.json()['items']
        for repo in repo_list:
            repo_name = repo['html_url']
            desc = {
                'repo_desc': repo['description'],
                'star': repo['stargazers_count'],
                'is_show': REPO_SHOW
            }

            #if REDIS.hsetnx('repos', repo_name, json.dumps(desc)):
            download_dataset(repo_name)
            print(repo_name)
        time.sleep(10)


if __name__ == '__main__':
    keywords = ['bl_info']
    #REDIS.set('keywords', ' '.join(keywords))
    for keyword in keywords:
        search_github(keyword)
