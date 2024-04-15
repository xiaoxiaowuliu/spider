#!/usr/bin/p3
from lxml import etree
from selenium import webdriver
from threading import Thread
import json
import requests

class NeteaseSpider:
  def __init__(self):
    opt = webdriver.chrome.options.Options()
    opt.add_argument('--headless')
    opt.add_argument('lang=zh_CN.UTF-8')
    opt.add_argument('blink-settings=imagesEnabled=false')
#    driverPath = "E:\virtualbox_share\chromedriver.exe"
    self.driver = webdriver.Chrome(chrome_options=opt)
    self.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
  def getHtmlFromFile(fileName):
    with open(fileName,"r",encoding='utf-8') as f:
      data = f.read()
    return data
    
  def getHtmlFromURL(url):
    self.driver.get(url)
    self.driver.switch_to.frame('g_iframe')
    html = self.driver.page_source
    return html

  def paraseMusic(html):
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
    
  #def downloadMusic(self,title,time,singer,link):
  def downloadMusic(self,**kwargs): 
    print(kwargs['title']," downloading... ")
    res = requests.get(kwargs['link'],headers=self.headers)
    if res.status_code == 200:
      titleStr = str(kwargs['title']).replace('/',',')
      singerStr = str(kwargs['singer']).replace('/',',')
      saveName = titleStr+"-"+singerStr+".mp3"
      with open(saveName,"wb") as f:
        f.write(res.content)
      print(titleStr+" download successful") 
    else:
      print(kwargs['title']+" download failure")  
    
    
  def crawl(self,url):
    print('---start---')
    '''
    html = self.getHtmlFromURL(url)
    with open("netmusic.html","w",encoding='utf-8') as f:
      f.write(html)
    '''
    '''
    html = self.getHtmlFromFile("netmusic.html")
    musics =self.paraseMusic(html)
    
    with open("netmusic.log","w", encoding="utf8") as f:
      json.dump(musics,f,ensure_ascii=False)      
    '''
    with open("netmusic.log","r", encoding="utf8") as f:
      musicList = json.load(f)
      
    for m in  musicList:
      Thread(target=self.downloadMusic,kwargs=m).start()
      
      
   
if __name__ == '__main__':
  spider = NeteaseSpider()
  url  = "https://music.163.com/#/discover/toplist?id=3779629"
  spider.crawl(url)
