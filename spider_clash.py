import requests
from lxml import etree
from selenium import webdriver
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


class Clash:
  def __init__(self):
    self.head = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
    self.date = str(datetime.now().year)+"-"+str(datetime.now().month)+"-"+str(datetime.now().day)   
    
    
  def getCurrentDayURL(self,url1):
    res = requests.get(url1,headers=self.head)
    url = ""
    if res.status_code == 200:
      doc = etree.HTML(res.text)
      links = doc.xpath(f'//a[contains(@href,"{self.date}")]')
      if len(links) == 0:
        self.date=str(datetime.now().year)+"-"+str(datetime.now().month)+"-"+str(datetime.now().day-1)
        links = doc.xpath(f'//a[contains(@href,"{self.date}")]')
      url2 = links[0].get('href')    
      url=url1.replace("/free-nodes","")+url2
      print("get url: "+url)
    return url           
      
      
  def getClashUrl(self,url):
    clashURL = self.getCurrentDayURL(url)
    res = requests.get(clashURL,headers=self.head)
    if res.status_code == 200:
      print("spider "+clashURL)
      doc = etree.HTML(res.text)
      pElements = doc.xpath(f'//p[contains(text(),".yaml")]')
      fileName = "clash_"+self.date+".txt"
      with open(fileName,"a+",encoding='utf-8') as fw:
        for p in pElements:
          print(p.text)
          fw.write(p.text+"\n")
          #self.saveFile(fileName,p.text)
    else:
      print (f'{url} not avaiable')
    
      
  def saveFile(fileName,data,encoding='utf-8'):
    with open(fileName,"a+",encoding=encoding) as fw:
      fw.write(data)      
  
  def craw(self,urls:list):
    thread=[]
    with ThreadPoolExecutor(max_workers=4) as p:
      for url in urls:
        thread.append(p.submit(self.getClashUrl,url))
    wait(thread,return_when=ALL_COMPLETED)
    print("done")    
       
if __name__ == '__main__':
  urls=['https://clashnode.github.io/free-nodes','https://clashnodeshare.github.io/free-nodes','https://nodeclash.github.io/free-nodes','https://clashgithub.github.io/free-nodes']
  clash = Clash() 
  clash.craw(urls)
  
  
  
  
  