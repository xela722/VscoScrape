# README #


### VSCO Scraper/ VSCO Crawler ###


## Input ##
# Method 1: Command Line #
Run: scrape.py user1,user2


# Method 2: From Another Python Script #
1. from scrape import crawl_users
2. crawl_users(['user1', 'user2'])
3. crawl_users(['user1', 'user2'], output_dir)

## Ouptut ##
* Files will be saved in the programs local directory
* Each user will have a folder created under a root 'vsco' folder: "vsco\username"
* Files that have already been downloaded will be skipped on subsequent runs



### Requirements ###
Run: pip install -r requirements.txt
* python 2.7 (for now)
* requests
* beautifulsoup4