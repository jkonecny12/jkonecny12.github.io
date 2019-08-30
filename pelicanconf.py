# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Jiri Konecny'
SITENAME = "Dragon's Lair"
SITESUBTITLE = "With an age it comes the wisdom. Wise is the one who listens."
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Prague'

DEFAULT_LANG = 'en'

# Theme and theme config
THEME = "./themes/Flex"
SITELOGO = "/images/avatar.jpg"
DISQUS_SITENAME = "packetseekers"
MAIN_MENU = True
USE_FOLDER_AS_CATEGORY = True
MENUITEMS = (
    ('Categories', '/categories.html'),
    ('Tags', '/tags.html'),
)
PYGMENTS_STYLE = 'github'
BROWSER_COLOR = '#333'
# End theme and theme config

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
# LINKS = (('Pelican', 'http://getpelican.com/'),
#          ('Python.org', 'http://python.org/'),
#          ('Jinja2', 'http://jinja.pocoo.org/'),
#          # ('You can modify those links in your config file', '#'),
#          )

STATIC_PATHS = ['images']

# Social widget
# SOCIAL = (('You can add links in your config file', '#'),
#           ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
