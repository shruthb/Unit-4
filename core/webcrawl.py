import sys
import re
import urllib2
import urlparse
import extract_class
import threading
from bs4 import BeautifulSoup

loc = threading.Lock()

class crawler(threading.Thread) :
    def __init__(self,url,depth=3):
        threading.Thread.__init__(self)
        self.crawled = set([])
        self.seed = url
        self.webwork = extract_class.website(url,[])
        self.depth = depth
        self.tabfile = open("usethis.tab","a")

    def writetab(self,res) :
        loc.acquire()
        attrs = ['url','media queries','geolocation','local storage','camera','touch']
        #{"url":url,"media queries":m,"geolocation":g,"local storage":l,"camera":c,"touch":t}
        for each in res :
            if each :
                for attr in attrs :
                    self.tabfile.write(str(each[attr])+'\t')
                self.tabfile.write('\n')
        loc.release()
        
    def run(self):
        'crawls the web seed - must be a string, single domain for optimizing other stuff'
        tocrawl = set([self.seed])
        notendRe = re.compile("\.(pdf|zip|gif|rss|jpg)\s*$")
        for i in range(self.depth) : 
            foundcrawl = set([])
            res = []
            for crawling in tocrawl :
                print "CRAWLING :", crawling
                url = urlparse.urlparse(crawling)
                try:
                    response = urllib2.urlopen(crawling)
                    content = response.read()
                except:
                    print "could not open %s" % crawling
                    continue
                soup = BeautifulSoup(content)
                res.append(self.webwork.process('http://'+url[1]+url[2],soup)) 
                #mon.put(res) #print res#put res into the database
                
                self.crawled.add(crawling)
                    
                for link in soup.find_all("a", href=re.compile(".+")):
                    link = link['href']
                    if notendRe.search(link) or link=='/':
                        #print 'end : ',link
                        continue
                    if link.startswith('/'): #relative
                        link = 'http://' + url[1] + link
                    elif link.startswith('#') or link.startswith("mailto"): #something on the same page
                        continue
                    elif not link.startswith('http'):
                        link = urlparse.urljoin(url.geturl(),link)
                    if link not in self.crawled: #link belong to same domain - link.find(url[1])!=-1 and
                        foundcrawl.add(link)
                        #print link
                #raw_input()
            if res:
                self.writetab(res)
            #print 'found : ',foundcrawl
            #x =  raw_input("press enter")
            tocrawl = foundcrawl
        self.tabfile.close()


if __name__=='__main__':
    '''main for testing '''
    if len(sys.argv) < 2:
        sys.argv += ["http://www.about.com/#!/editors-picks/"]#"http://www.pes.edu","http://www.ourairports.com/",
                     #"http://www.mit.edu","http://www.asp.net","http://maps.google.com",
                     #"http://www.dolectures.com/","http://www.about.com/#!/editors-picks/"]
        #sys.argv += ["http://www.dolectures.com/","http://snapbird.org"]
    t = []
    for each in sys.argv[1:] :
        t.append(crawler(each)) #pass a single url at a time
        t[-1].start()
        
    for i in t :
        i.join()

'''
def process(url,features):
    if not url.startswith("http"):
        url = "http://" + url
    t = crawler(url,1)
    t.start()
    t.join()
'''
