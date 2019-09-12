class DCDataBean:
   
   def __init__(self, dcType, ip , totalNumber):
      self.dcType=dcType
      self.ip=ip
      self.totalNumber=totalNumber 
       
   def create(self, dcType, ip , totalNumber):
       self.dcType=dcType
       self.ip=ip
       self.totalNumber=totalNumber 
     
 
      
   def toString(self):
       return "{dcType:"+dcType+",ip:"+ip+",totalNumber:"+str(totalNumber)+"}"