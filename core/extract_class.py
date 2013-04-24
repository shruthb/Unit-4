import re
import urllib2, urlparse
from bs4 import BeautifulSoup

class website(): #threading.Thread

    def __init__(self,baseurl,features):
        self.url = baseurl
        self.features = features
        self.domCss = {} # dict of external css sheets for page, string : tuple of attr
        self.domScripts = {} # key = script url, val = content of script url

    def getContent(self,relurl):
        "gets script/style content from link tag's href or @import's url()"
        if relurl.startswith('/'):
            link =  self.url+ relurl
        elif relurl.startswith("http"):
            link = relurl
        else: #not sure - error was because of href="domain.css" which is relative but doesn't start with /
            link = urlparse.urljoin(self.cururl,relurl)
        try :
            #print link
            resp = urllib2.urlopen(link)
            content = resp.read()
            return content
        except : 
            print "Couldn't open link"
            return ''
    
    #findall - list of groups=strings

    def atMedia(self,cssContent):
        "searches for @media rules in css content"
        #mediaType = "((only |not )?(?P<mediaType>braille|embossed|handheld|print|projection|screen|speech|tty|tv|all) (and|,))*?" #
        mediaFeature = re.compile("width|height|device-width|device-height|orientation|aspect-ratio|device-aspect-ratio|color|color-index|monochrome|resolution|scan|grid")
        mediaAtRule = re.compile("@media\s(?P<mediaQuery>.*?){[^}]*?}") #@media rule within style tag or imported doc
        #mediaAtRule = re.compile("@media (?P<media>[^{]*?){[^}]*?}") #@media rule in .css file 
        count = 0 #len(mediaAtRule.findall(cssContent))
        for meq in mediaAtRule.finditer(cssContent) :
            if mediaFeature.search(meq.group(1)):
                count += 1
        return count


    def get_external_css(self, soup) : #,css 
        "get css which is specified using link tag and check it for media queries"
        #print "External css : "
        extStyles = soup.findAll("link", href=re.compile("(.+?\.css).*?"))
        #extStylesRe = re.compile("<link (.*?href=['\"](.*?\.css).*?['\"].*?)\s?/>")  #link to external style sheet
        mediaFeature = re.compile("width|height|device-width|device-height|orientation|aspect-ratio|device-aspect-ratio|color|color-index|monochrome|resolution|scan|grid")
        #mediaAttrRe = re.compile("media=\"(?P<mediaFeature>.*?)\"") #media type - link's attr

        mediaCount = 0
        #print extStyles
        for estyle in extStyles :
            #print estyle
            meq = str(estyle.get('media'))
            if estyle['href'] in self.domCss.keys():
                mediaCount += self.domCss[estyle['href']][1];
            elif meq and mediaFeature.search(meq):
                #print "media in link tag"
                mediaCount += 1
                self.domCss[estyle[1]] = ['',1]
            else : #not extracting if media="" was already in link tag
                #print "getting style page"
                cssContent = self.getContent(str(estyle['href']))
                count = self.atMedia(cssContent)
                #css.append(cssContent)
                mediaCount += count
                self.domCss[estyle['href']] = (cssContent,count) #or []
                #print "css content : \n",cssContent, mediaCount
            
        return mediaCount


    def get_import_media(self,cssContent) : #,css
        "get css which is specified using @import rule and check it for media queries"
        importAtRe = re.compile("@import url\(['\"](.*?\.css).*?['\"]\)(?P<media>.*?);") #@import rule within style tag with media spec
        mediaFeature = re.compile("width|height|device-width|device-height|orientation|aspect-ratio|device-aspect-ratio|color|color-index|monochrome|resolution|scan|grid")
        mediaCount = 0
        for each in importAtRe.findall(cssContent):
            if each[0] in self.domCss.keys():
                mediaCount += self.domCss[each[1]][1]
            elif each[1] and mediaFeature.search(each[1]):
                mediaCount += 1
                self.domCss[each[1]] = ('',1)
            else:
                cssContent = self.getContent(each[0])
                #css.append(cssContent)
                count = self.atMedia(cssContent)
                mediaCount += count
                self.domCss[each[0]] = (cssContent,count) #or []
                #print "css content : \n",cssContent
        return mediaCount


    def get_internal_css(self, soup):
        "get css which is written within style tag and check it for media queries"
        styles = soup.find_all("style",type="text/css") #internal style tag
        #re.compile("<style type=\"text/css\">(.*?)</style>") 
        
        mediaCount = 0
        #print "internal css / css page : ", styles
        for style in styles :
            each = str(style.string)
            mediaCount += self.atMedia(each)    
            mediaCount += self.get_import_media(each)
        return mediaCount


    def mediaQueries(self, soup):
        "check the page for media queries"
        #css = []
        count = self.get_external_css(soup) #,css
        count += self.get_internal_css(soup) #,css
        if count>1 :
            return True
        else:
            return False
        
        
    def camera(self, soup, script):
        "check if the capture attribute is used for media capture"
        getmedRe = re.compile("navigator\.[a-z]*?[gG]etUserMedia\(")
        def captre(tag) :
            return tag.has_key('capture')
        for each in script :
            if getmedRe.search(each) :
                return True
        if soup.find_all(captre):
            return True
        else:
            return False


    #\s?(?P<lang>type=\"text/javascript\")?

    def getscript(self, soup):
        "get script from page - script tag content and external src"
        common = ["http://ajax.googleapis.com/ajax/libs/jquery/1.8/jquery.min.js",
                  "http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js?ver=1.7.1"]
        #scriptre = re.compile("<script.*?>(.+?)</script>",re.DOTALL)
        script_tags = soup.find_all("script") #scriptre.findall(page)
        #print script_tags
        #scriptlinksre = re.compile("<script .*?src=['\"](.*?\.js.*?)['\"].*?></script>")
        script_links = [] #scriptlinksre.findall(page)
        scripts = []
        #print "finding links"
        for each in script_tags :
            #print type(each)
            if each.get('src'):
                script_links.append(str(each['src']))
            else :
                scripts.append(str(each.get_text)) #each.string
        #print "scriptlinks : ",script_links
        for each in script_links :
            if each not in common :
                if each in self.domScripts.keys() :
                    scripts.append(self.domScripts[each])
                else :
                    scriptContent = self.getContent(each)
                    scripts.append(scriptContent)
                    self.domScripts[each] = scriptContent
        #print len(script_links),#'\n',scripts
        return scripts

    def localstorage(self,script):
        "check if the localStorage api is used by the page"
        locstore = re.compile("(window\.)?localStorage.?")
        for each in script :
            if locstore.search(each) :
                return True
        return False

    def geolocation(self,script):
        "check if the geolocation api is used by the page"
        geore = re.compile("(window\.)?navigator.geolocation")
        for each in script :
            if geore.search(each) :
                return True
        return False

    def touch(self, soup, script):
        "check if the touch event is used by the page"
        touchre = re.compile("(\.addEventListener\([\"']touch(start|move|end|cancel)[\"'])|(\.ontouch(start|move|end|cancel)=)")
        def registers_touch(tag):
            return tag.has_key('ontouchstart') or tag.has_key('ontouchmove') or tag.has_key('ontouchend') or tag.has_key('ontouchcancel')
        #touchpagere = re.compile("ontouch(start|move|end|cancel)")
        if soup.find_all(registers_touch) : #touchpagere.search(soup) :
            return True
        for each in script :
            if touchre.search(each) :
                return True
        return False
        
    def process(self, url, soup): #url here = baseurl + path
        "process url for the various features"
        try :
            self.cururl = url
            m = self.mediaQueries(soup)
            script = self.getscript(soup)
            g = self.geolocation(script)
            l = self.localstorage(script)
            c = self.camera(soup, script)
            t = self.touch(soup, script)
            return {"url":url,"media queries":m,"geolocation":g,"local storage":l,"camera":c,"touch":t}
        except Exception:
            return None
        #css = getcss(url,page)
        #ss = screensize(page)
        #add result to database
    
if __name__=='__main__':
    w = website('http://www.about.com',[])
    doc = urllib2.urlopen('http://www.about.com') #crawling)
    content = doc.read()
    #doc = open("dolec.txt")
    #content = doc.read()
    print content[:100]
    res = w.process('www.about.com',BeautifulSoup(content))
    for each in res:
        print each, res[each]
    #maps.google.com , www.ourairports.com, www.dolectures.com
    #note - send split url to process
