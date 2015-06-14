#  utils.py
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

from datetime import datetime

def fix_date(x, loader_context):
    '''Loader Context aware conversion of a date from one format to another.'''
    in_fmt = loader_context.get('date_fmt_in')
    out_fmt = loader_context.get('date_fmt_out')

    try:
        return datetime.strptime(x, in_fmt).strftime(out_fmt)
    except ValueError:
        return ''
