
training_doc=[{'url':'http://www.dolectures.com/','media queries': True,'geolocation':False ,'local storage':False,'camera':False,'touch':False,'mobcomp':True},{'url':'http://www.asp.net/downloads','media queries': True,'geolocation':False ,'local storage':False,'camera':False,'touch':False,'mobcomp':True},{'url':'http://www.asp.net/community','media queries': True,'geolocation':False ,'local storage':False,'camera':False,'touch':False,'mobcomp':True},{'url':'http://login.asp.net/login/signin.aspx','media queries': False,'geolocation':False ,'local storage':False,'camera':False,'touch':False,'mobcomp':False},{'url':'http://www.alistapart.com/topics','media queries': True,'geolocation':False ,'local storage':False,'camera':False,'touch':False,'mobcomp':True}]
'''
creating data set of the format supported by Orange
'''
sample = open("newsam1.tab","w")
sample.write("url\t")

allfeats = ["media queries","geolocation","local storage","camera","touch"]
for feat in allfeats :
    sample.write(feat+'\t')

sample.write("mobcomp\n")
sample.write("d\td\td\td\td\td\td\n")
sample.write("\t\t\t\t\t\tclass\n")

for doc in training_doc:
        sample.write(str(doc['url'])+'\t'+str(doc['media queries'])+'\t'+str(doc['geolocation'])+'\t'+str(doc['local storage'])+'\t'+str(doc['camera'])+'\t'+str(doc['touch'])+'\t'+str(doc['mobcomp'])+'\n')
'''
this file contains the result of crawling the web
'''
file1=open("usethis.tab","r")
count=1
for eachline in file1:
    sample.write(eachline)
