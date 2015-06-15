#  r-nsaleaks-wiki2list.py
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

"""
Input:  r/NSALeaks/wiki/timeline markup
Output: list of urls

Usage:
    r-nsaleaks-wiki2list.py <wikifile> [-o <outfile>]
    r-nsaleaks-wiki2list.py (-h | --help)
    r-nsaleaks-wiki2list.py --version

Options:
    -h --help     Show this screen.
    --version     Show version.
    -o <outfile>  Optionally output to file [default: STDOUT].
"""

from docopt import docopt
import sys, re

def main(args):
    l = file_to_list(args['<wikifile>'])
    f = sys.stdout
    if args['-o'] != 'STDOUT':
        f = open(args['-o'], 'a')
    try:
        for url in l:
            print>>f, url
    except IOError:
        pass
    finally:
        try:
            f.close()
        except IOError:
            pass

def file_to_list(fname):
    l = []
    match_url = re.compile("\*.+\]\(([^)]+)\)")
    with open(fname) as f:
        for line in f:
            url = match_url.match(line)
            if url:
                l.append(url.groups()[0])

    return l

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.0.1')
    main(arguments)
    sys.exit(0)

