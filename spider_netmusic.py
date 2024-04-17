#!/usr/bin/p3
from lxml import etree
from selenium import webdriver
from spider_download import Download
from concurrent.futures import ThreadPoolExecutor,as_completed
import json


class NeteaseSpider:
  def __init__(self):
    opt = webdriver.chrome.options.Options()
    opt.add_argument('--headless')
    opt.add_argument('lang=zh_CN.UTF-8')
    opt.add_argument('blink-settings=imagesEnabled=false')
    
    self.driver = webdriver.Chrome(chrome_options=opt)
    
    
  def getHtmlFromFile(self,fileName):
    with open(fileName,"r",encoding='utf-8') as f:
      data = f.read()
    return data
    
  def getHtmlFromURL(self,url):
    self.driver.get(url)
    self.driver.switch_to.frame('g_iframe')
    html = self.driver.page_source
    return html
    
  def getHtmlFromFileWithLogin(self,url):
    with open("cookie.txt","r", encoding="utf8") as f:
      cookies = json.load(f)
    self.driver.delete_all_cookies()
    self.driver.get(url)
    for c in cookies:
      self.driver.add_cookie(c)
    html = self.getHtmlFromURL(url)
    return html
  
  def paraseMusic(self,html):
    htmlElem = etree.HTML(html)
    musicsList = list()
    #歌单名称
    playlistName = htmlElem.xpath('/html/body/div[3]/div[2]/div/div[1]/div/div[2]/div/div[1]/h2/text()')
    #歌曲数量
    musicNum = htmlElem.xpath('/html/body/div[3]/div[2]/div/div[2]/div[1]/span/span/text()')
    #播放次数
    playNum = htmlElem.xpath('//*[@id="play-count"]/text()')
    #歌单链接
    link = playLink = htmlElem.xpath('/html/head/link[1]/@href')
    playlistDic = {'title':playlistName,"time":musicNum,"singer":playNum,'link':link}
    musicsList.append(playlistDic)
    
    #all title
    
    musicsTitle = htmlElem.xpath("//td[2]/div/div/div/span/a/b/@title")
    #all time
    musicsTime = htmlElem.xpath("//td[3]/span/text()")
    #all singer
    musicsSinger = htmlElem.xpath("//td[4]/div/@title")
    #all link ?
    musicsLink = htmlElem.xpath("//td[2]/div/div/div/span/a/@href")
    
    for i in range(0,len(musicsTitle)):
        link = "https://music.163.com/song/media/outer/url"+str(musicsLink[i]).replace('/song','')+".mp3"
        musicDic = {'title':musicsTitle[i],'time':musicsTime[i],'singer':musicsSinger[i],'link':link}
        print(musicDic)
        musicsList.append(musicDic)
    return musicsList  
    
  def crawl(self,url):   
    '''
    #html = self.getHtmlFromURL(url)
    html = self.getHtmlFromFileWithLogin(url)    
    with open("netmusic_login.html","w",encoding='utf-8') as f:
      f.write(html)
    '''
    
    '''    
    html = self.getHtmlFromFile("netmusic_login.html")
    musicsList =self.paraseMusic(html)
    
    with open("netmusic_login.log","w",encoding="utf8") as f:
      json.dump(musicsList,f,ensure_ascii=False)      
    '''
    
    with open("netmusic_login.log","r", encoding="utf8") as f:
      musicList = json.load(f)
      
        
    futures = []
    download = Download()
    with ThreadPoolExecutor(max_workers=5) as p:    
      for m in musicList:
        musicName = str(m['title']+"_"+m['singer']+".mp3").replace('/',',')
        musicURL = m['link']
        futures.append(p.submit(download.streamDownload,musicName,musicURL))
    try:
      with open("download_success_list.txt","w",encoding="utf-8") as fs,open("download_fail_list.txt","w",encoding="utf-8") as ff:
        for future in as_completed(futures):
          file = future.result()
          if str(file).startswith("+"):
            ff.write(file.replace("+","")+"\n")
          else:
            fs.write(file+"\n")        
    except Exception as e:
      print(e)
    
      
if __name__ == '__main__':
  spider = NeteaseSpider()
  url  = 'https://music.163.com/#/my/m/music/playlist?id=28659883'
  spider.crawl(url)
