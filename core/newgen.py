from pymongo import Connection
import Orange
 
connection1=Connection()    #making a connection
db1=connection1.url_database1  #getting a database
newcollection=db1.url_newcollection #getting a collection



data=Orange.data.Table("newsam1")
learner = Orange.classification.bayes.NaiveLearner()
classifier = learner(data)
i=1
attr=['url','media queries','geolocation','local storage','camera','touch']
li=[]

for d in data[5:]:
    c = classifier(d)
    d['mobcomp']=c
    li.append(d)



#print li
newli=[]
l=[]
rfile=open("usethis.tab","r")
for eachline in rfile:
    li=eachline.split("\t")
    l.append(li)

#print l


for each in l:
    doc1={}
    doc1['url']=each[0]
    doc1['media queries']=each[1]
    doc1['geolocation']=each[2]
    doc1['local storage']=each[3]
    doc1['camera']=each[4]
    doc1['touch']=each[5]
    doc1['mobcomp']=d['mobcomp'].value
    #the moment i add the rhs it gives orange format string how do get just true or false
    newli.append(doc1)
#print newli

#li is list of dicts

newcollection.insert(newli)
'''
#prints all doc with media query true
for i in newcollection.find({'media queries':'True'}):
    print i
'''


