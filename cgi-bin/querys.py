import cgi, threading
from pymongo import Connection

connection1=Connection()    #making a connection
db1=connection1.url_database1  #getting a database
newcollection=db1.url_newcollection #getting a collection

print "Content-type: text.html\r\n\r\n"
print ""
print "<html><head><title>"
print "Output</title></head><body>"

#removes the unicode format
def formatres(resdict):
    del resdict[u'_id']
    new={}
    for each in resdict.keys():
        new[str(each)]=str(resdict[each])
    return new

form = cgi.FieldStorage()
url = form.getvalue("url")
res = newcollection.find_one({'url': url})

if not res :
   print "<h2>We haven't crawled ",url,"yet!</h2>"
   print "<div> Please get back later </div>"
   #mon.needtocrawl(url)
   
else :
   print 'result!!!!!'
   #print res
   ans=formatres(res)
   if ans['mobcomp']=='True':
       print '%s is mobile compatible'%(url)
   else:
       print '%s is not mobile compatible'%(url)


print "</body></html>"
     
