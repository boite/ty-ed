# -*- coding: utf-8 -*-
#
#  eff.py Spider for EFF Primary Sources
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

import scrapy

from ed_docinfo.items import EdDocinfoItem
from ed_docinfo.loaders import EFFEdDocLoader

class EffSpider(scrapy.Spider):
    '''Scrape information from EFF about Ed Snowden Primary Sources.

    Start at /nsa-spying/nsadocs and create an item from each row in the table
    there. Complete each item, with info about EFF's instance of each Primary
    Source, by following a link in the table to dedicated page under /documents/.
    ''' 
    name = 'eff'
    allowed_domains = ['www.eff.org']
    start_urls = ['https://www.eff.org/nsa-spying/nsadocs']

    def parse(self, response):
        '''Create items from rows in the table before requesting the docpages'''
        for row in response.xpath('//table[contains(concat(" ", @class, '
                                  '" views-table "), " ")]/tbody/tr'):
            l = EFFEdDocLoader(item=EdDocinfoItem(), selector=row)
            l.add_value('src', self.name)
            # first cell: date
            l.add_xpath('pubdate', 'td[1]/text()')

            # last cell: link to publication
            l.add_xpath('publisher_url', 'td[contains(concat(" ", @class, '
                        '" views-field-name "), " ")]/em/a/@href')

            # middle cell: link to page under /documents/
            docpage_href_node = row.xpath('td[contains(concat(" ", @class, '
                                        '" views-field-title "), " ")]/a/@href')

            try:
                request = scrapy.Request(docpage_href_node.extract()[0],
                                         callback=self.parse_docpage)
            except IndexError:
                # there's no docpage_url to follow
                #l.add_xpath('title', 'td[contains(concat(" ", @class, '
                #                     '" views-field-title "), " ")]/text()')
                # some repugnant shit: the above doesn't work, but this does
                l.add_xpath('title', 'td[2]/text()')
                yield l.load_item()
            else:
                l.add_xpath('title', 'td[contains(concat(" ", @class, '
                                     '" views-field-title "), " ")]/a/text()')

            # make the item available in the callback for this request
            request.meta['ed_item_ldr'] = l

            # request the docpage_url
            yield request

    def parse_docpage(self, response):
        '''Complete an item with info from the docpage response.'''
        l = response.meta['ed_item_ldr']
        l.add_value('instance_url',
                    response.xpath('//span[@class="file"]/a/@href').extract())
        return l.load_item()
