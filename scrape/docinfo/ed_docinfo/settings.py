# -*- coding: utf-8 -*-

# Scrapy settings for ed_docinfo project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ed_docinfo'

SPIDER_MODULES = ['ed_docinfo.spiders']
NEWSPIDER_MODULE = 'ed_docinfo.spiders'
DOWNLOAD_DELAY = 4


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Thank you Ed (https://github.com/boite/ty-ed)'

