# Input: is an array of VSCO usernames: can either call with "scrape.py user1,user2" or specify users in USERNAMES bellow and call "scrape.py"
# Output:
# if user has been crawled before, crawler will stop when link dates are less then the latest date in the output folder

# web
import requests
from bs4 import BeautifulSoup as bs
from urllib import urlretrieve

# file/folder ops
import errno
import os
from os import path
import sys

# threading
from threading import Thread
import Queue # queue in Python 3

from pprint import pprint



# Global variables
NUM_DL_THREADS = 10
ROOT = path.expanduser('~/Desktop/vsco/') # use . for local directory, ~ for user directory
DEBUG = False # dont download anything or create any directories
USERNAMES = []
q = Queue.LifoQueue()

def crawl_users(usernames = USERNAMES, output_root = ROOT):
    global ROOT
    ROOT = output_root

    if len(sys.argv) > 1:
        usernames = sys.argv[1].split(',')
        usernames = [x.strip() for x in usernames]

    print "Crawling VSCO Users:", usernames
    print "Output directory:", ROOT

    print "Starting {} download threads".format(NUM_DL_THREADS)
    start_download_threads(NUM_DL_THREADS)

    for username in usernames:
        print "Scraping vsco user: {}".format(username)
        crawl_username_for_links(username)

    print "Joining download threads..."
    q.join()
    print "Done."


def crawl_username_for_links(username):
    global q

	
    url = "http://vsco.co/{}/images/1".format(username)

    headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"}

    p = requests.get("http://vsco.co/content/Static/userinfo",headers=headers)
    r = requests.get(url, headers=headers)
    if (r.status_code != 200):
        print "Error: {}. Check username: {}".format(r.status_code, username)
        return -1


    soup = bs(r.content,'html.parser').find('meta',property='al:ios:url')
		
    vs = p.cookies['vs']
    site_id = soup['content'].replace('vsco://user/', "").replace('/grid', "")
    page = 1
    firstpage = "http://vsco.co/ajxp/{0}/2.0/medias?site_id={1}&page={2}".format(vs, site_id, page) # what does this do? --> &size=%s    , sys.argv[2]

    headers = {'cookie': 'vs={}'.format(vs)}



    output_folder_path = path.join(ROOT,username)
    if path.isdir(output_folder_path):
        stop_date = get_latest_file_date(output_folder_path)
    else:
        stop_date = 0

    r = requests.get(firstpage, headers=headers)
    medias_json = r.json()['media']
    medias_json = sorted(medias_json, key=lambda date: date['image_status']['time'], reverse=True)

    links_found = len(medias_json)

    if (links_found > 0):
        if not DEBUG: mkdir_p(output_folder_path)

    while (links_found > 0):
        print "Page: {}, Found {} links".format(page,links_found)

        for i in medias_json:
            file_date = i['image_status']['time']
            if file_date > stop_date:
                q.put_nowait(i)
            else:
                print ("Stopping crawler for user: {}, file date: {} is less that stop date: {}".format(username, file_date, stop_date))
                return 1

        page += 1
        nextpage = "http://vsco.co/ajxp/{0}/2.0/medias?site_id={1}&page={2}".format(vs, site_id, page)
        r = requests.get(nextpage, headers=headers)
        medias_json = r.json()['media']
        medias_json = sorted(medias_json, key=lambda date: date['image_status']['time'], reverse=True)
        links_found = len(medias_json)

    return 0





def start_download_threads(num_threads):
    for i in range(num_threads):
        t = Thread(target=download_image)
        t.daemon = True
        t.start()

def download_image():
    while True:
        media_json = q.get()

        file_url = media_json['responsive_url'].replace("im.", "http://im.")
        date = media_json['image_status']['time']
        username = media_json['perma_subdomain']

        file_name = str(date)+'_'+ username + '_' +file_url.split('/')[-1]
        folder_path = path.join(ROOT, username)
        # if not DEBUG: mkdir_p(folder_path)
        file_path = path.join(folder_path, file_name)

        if path.isfile(file_path):
            print "File already exists, skipping: {}, Remaing links: {}".format(file_name, q.qsize())
        else:
            if not DEBUG: urlretrieve(file_url, file_path)
            print "Downloaded: {}, Remaing links: {}".format(file_name, q.qsize())
        q.task_done()


# @tzot https://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# date is in unix format, miliseconds to match vsco dates
def get_latest_file_date(folder_path):
    files = os.listdir(folder_path)
    file_paths = []
    for i in files:
        file_paths.append(path.join(folder_path, i))
    latest_file = max(file_paths, key=os.path.getctime)
    return int(os.path.getctime(latest_file)*1000)


if __name__ == '__main__':
    crawl_users()