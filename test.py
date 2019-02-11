import os
DIR = '/Users/caixuesen/Documents/PythonCrawler/wizb_Chinese'


print(len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]))