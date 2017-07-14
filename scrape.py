import requests
from bs4 import BeautifulSoup as bs
import sys
import urllib
import datetime

account = sys.argv[1]

url1 = "http://vsco.co/%s/images/1" % account

q = requests.get(url1)
vs=q.cookies['vs']

names=[]
times=[]
date = "null"

metas = bs(q.content,'html.parser').find('meta',property='al:ios:url')

site_id=metas['content'].replace('vsco://user/', "").replace('/grid', "")

mainUrl = "http://vsco.co/ajxp/%s/2.0/medias?site_id=%s&page=1&size=%s" % (vs, site_id, sys.argv[2])

headers = {'cookie': 'vs=%s' % vs}

opener = urllib.URLopener()
print "Scraping VSCO: %s" % (account)
r = requests.get(mainUrl, headers=headers)
imgs = []

for arg in range(0,len(sys.argv)):
    if sys.argv[arg]=="-ds":
        date="used"
        dateStart=sys.argv[arg+1]
    if sys.argv[arg]=="-de":
        date="used"
        dateEnd=sys.argv[arg+1]


for i in range(0, len(r.json()['media'])-1):
    try:
        str(imgs.append(r.json()['media'][i]['responsive_url']))
	str(names.append(str(datetime.datetime.fromtimestamp(int(r.json()['media'][i]['image_status']['time'])/1000).strftime('%Y-%m-%d %H:%M:%S')).replace(":",".")))
    except:
        print "Exception!"
        continue


for x in range(0, len(imgs)-1):
    try:
        if date!="null":
            reqUrl = str(imgs[x])
            use = reqUrl.replace("im.", "http://im.")
            if dateEnd in names[x]:    
                urllib.urlretrieve(str(use), "vsco %s.jpg" % (names[x]))
                print "%s Downloaded" % (names[x])
                date="null"
            else:
                 continue
        else:
            if dateStart in names[x]:
                reqUrl = str(imgs[x])
                use = reqUrl.replace("im.", "http://im.")

                urllib.urlretrieve(str(use), "vsco %s.jpg" % (names[x]))
                print "%s Downloaded" % (names[x])
                break
            else:
                reqUrl = str(imgs[x])
                use = reqUrl.replace("im.", "http://im.")

                urllib.urlretrieve(str(use), "vsco %s.jpg" % (names[x]))
                print "%s Downloaded" % (names[x])
    except:
        print "EXCEPT!!!"
        continue
