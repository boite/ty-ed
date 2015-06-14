#  loaders.py Custom ItemLoader definitions.
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

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Identity, TakeFirst, MapCompose
from ed_docinfo.utils import fix_date
from string import whitespace

class EdDocLoader(ItemLoader):
    # don't do input processing
    default_input_processor = Identity()
    # most fields will have just one value
    default_output_processor = TakeFirst()
    # although instance_url shall be a list
    instance_url_out = Identity()

    title_in = MapCompose(lambda x: x.strip())
    publisher_url_in = MapCompose(lambda x: x.strip())


class CFEdDocLoader(EdDocLoader):
    # pubdate is somewhat inconsistent: on top of stripping some chars it is
    # necessary to remove whitespace from within the date before converting
    pubdate_in = MapCompose(lambda x: x.rsplit(',', 1)[-1],
                            lambda x: x.strip(',.' + whitespace),
                            lambda x: ''.join(x.split()),
                            fix_date,
                            date_fmt_in='%d%B%Y', date_fmt_out='%Y-%m-%d')

class EFFEdDocLoader(EdDocLoader):
    
    pubdate_in = MapCompose(lambda x: x.strip(),
                            fix_date,
                            date_fmt_in='%m/%d/%Y', date_fmt_out='%Y-%m-%d')
