# -*- coding: utf-8 -*-
#
#  cy.py Spider for Courage Foundation Snowden's Revealed documents.
#  Copyright (C) 2015 jah
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see
#  <http://www.gnu.org/licenses/>.

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from ed_docinfo.items import EdDocinfoItem
from ed_docinfo.loaders import CFEdDocLoader


class CfSpider(CrawlSpider):
    name = 'cf'
    allowed_domains = ['edwardsnowden.com']
    start_urls = ['https://edwardsnowden.com/category/revealed-documents/page/1/']

    rules = (
        Rule(LinkExtractor(restrict_xpaths=r'//div[@class="nav-previous"]')),
        Rule(LinkExtractor(
            restrict_xpaths=r'//article/header/h1[@class="entry-title"]'),
            callback='parse_item'
        ),
    )

    def parse_item(self, response):
        '''Create an item from the info in this response.'''
        l = CFEdDocLoader(item=EdDocinfoItem(), response=response)
        l.add_value('src', self.name)

        l.add_xpath('title', '//article/header/h1[@class="entry-title"]/text()')

        l.add_xpath('publisher_url', '//div[@class="entry-content"]/'
                                     'p[position()=1]/a[last()]/@href')

        l.add_xpath('pubdate', '//div[@class="entry-content"]/p[position()=1]/'
                               'a[last()]/following-sibling::text()')

        l.add_xpath('instance_url', '//div[@class="entry-content"]/p[last()]'
                                    '/a/@href')

        return l.load_item()
