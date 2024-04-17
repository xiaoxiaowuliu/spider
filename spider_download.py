import requests
from concurrent.futures import ThreadPoolExecutor,as_completed
from tqdm import tqdm


class Download:
  def __init__(self):
    self.headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
  
  #计算分块地址
  def calDiviRange(fileSize,blockNum=10):
    blockSize = fileSize//blockNum
    arr = list(range(0,fileSize,blockSize))
    result = []
    for i in range(len(arr)-1):
      s_pos,e_pos = arr[i],arr[i+1]-1
      result.append([s_pos,e_pos])
    result[-1][-1] = fileSize-1
    return result

  #下载部分文件  
  def downloadRange(fileName:str,fileURL:str,s_pos:int,e_pos:int):
    head = {"Range":f'bytes={s_pos}-{e_pos}'}
    res = requests.get(fileURL,headers=head,stream=True)
    with open(fileName,"ab+") as f:
      for chunk in res.iter_content(chunk_size=128):
          f.write(chunk)
        
  #分块式下载        
  def framentDownload(fileName:str,url:str):
    res = requests.head(url,headers=self.headers)  
    fileSize = int(res.headers['Content-Length'])
    print(f'{fileName} length: {fileSize}')
    divRanges = calDiviRange(fileSize)
    if res.status_code == 200:
      with ThreadPoolExecutor(max_workers=8) as p:
        futers = []
        for s_pos,e_pos in divRanges:
          futers.append(p.submit(downloadRange,fileName,url,s_pos,e_pos))
          
      for f in as_completed(futers):
        print(f'{fileName} bolck download successful')  
    else:
      print(f'{fileName} downloading failure')   
    return fileName
  
  #流式下载          
  def streamDownload(self,fileName:str,url:str):  
    res = requests.get(url,headers=self.headers,stream=True)
    if res.status_code == 200:
      #fileSize = int(res.headers['Content-Length'])
      fileSize =  len(res.content)/1024/1024
      print("%s length %.2f MB" %(fileName,fileSize))
      if fileSize > 1 :  
        total = 0
        with open(fileName,"wb") as f:
          for chunk in tqdm(res.iter_content(chunk_size=128),total=fileSize//128,unit='b',unit_scale=True):
            f.write(chunk)
            #total += f.write(chunk)
            #print(total/musicSize*100,"%")
        print(f'{fileName} downloading successful')
      else:
        print(f'{fileName} downloading failure')     
        fileName="+"+fileName
    else:
      print(f'{fileName} downloading failure') 
      fileName="+"+fileName
    return fileName
    