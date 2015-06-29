#  discodown.py  Combine discovered and downloaded document metadata.
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
Combine the output of source-discover.py and down.py to create a josn
file of Primary Source document metadata.

Usage:
    discodown.py  DISCO DOWN COMBI
    discodown.py  (-h | --help)
    discodown.py  --version

Arguments:
    DISCO  path to a json lines file as output by source-discover.py
    DOWN   path to a json lines file as output by down.py
    COMBI  output a json file to this path, overwrite it if it exists

Options:
    -h --help                        Show this screen.
    --version                        Show version.

"""

from docopt import docopt
import sys, json, copy

SCHEMA = {
    'pubdate': '',
    'url': '',
    'presentation_url': '',
    'published_files': [],
    'alternative_files': [],
    'accomp_articles': []
}
SCHEMA_ARTICLE = {
    'pubdate': '',
    'url': ''
}
SCHEMA_FILE = {
    'file': {
        'digest': '',
        'name': '',
        'original_name': '',
        'files': []
    },
    'index_type': '',
    'index': ''
}


def combine(disco, down=None, existing=None):
    '''Combine an item of discovered primary source info with an item
    of downloaded primary source info.

    An absence of downloaded primary source info will result in the
    creation of the same data structure as if the download info were
    present, but with an empty list of 'published_files'.

    A previously combined pair can be supplied as the 'existing'
    argument, in which case it will be appended with the appropriate
    discovered info, i.e. the downloaded info is assumed to already exist
    in 'existing' and is ignored.
    '''

    if existing:
        o = existing
    else:
        o = copy.deepcopy(SCHEMA)
        o['url'] = disco['url']
        o['pubdate'] = disco['pubdate']
        o['presentation_url'] = disco['presentation_url']
        if down:
            f = copy.deepcopy(SCHEMA_FILE)
            f['file']['digest'] = down['digest']
            f['file']['name'] = down['filename']
            f['file']['original_name'] = down['original_name']
            o['published_files'].append(f)

    a = copy.deepcopy(SCHEMA_ARTICLE)
    a['url'] = disco['article_url']
    a['pubdate'] = disco['article_pubdate']
    o['accomp_articles'].append(a)

    return o


def main(args):

    combined_count = 0

    # try to read and parse any previously combined entries.
    try:
        out_file = open(args['COMBI'], 'r')
    except IOError, e:
        combined = []
    else:

        try:
            combined = json.load(out_file)
        except ValueError, e:
            combined = []

        out_file.close()

    # combined map serves two purposes:
    # - store the combined records for writing to out_file.
    # - provide a lookup for previously combined entries.
    #   consumers need to test for the existence of an article url in
    #   and to retrieve the previosuly combined record.
    combined_map = {}
    for c in combined:
        ckey = c['url'] or c['presentation_url']
        combined_map[ckey] = {'record': c}
        combined_map[ckey]['articles'] = [
            art['url'] for art in c['accomp_articles']
        ]

    # read the discovery info into a lookup table of download urls.
    # a document can have more than one accompanying article (e.g. two
    # publishers collaborating on the publication of a document or
    # two articles by the same publisher which accompany an
    # overlapping set of documents), so the table maps download url to
    # article url to document info.
    #
    # where a download url is absent, create or update 'combined'
    # records from the document info alone. 
    discovered_map = {}
    disco_file = open(args['DISCO'], 'r')
    for line in disco_file:
        o = json.loads(line)
        url = o['url'] or o['presentation_url']
        art_url = o['article_url']
        if o['url']:
            if url not in discovered_map:
                discovered_map[url] = {}
            if art_url not in discovered_map[url]:
                discovered_map[url][art_url] = o
        else:
            # without a url, this doc cannot have been downloaded
            # so just create an entry from the discovery info
            if url not in combined_map:
                # new non-down record
                c = combine(o)
                combined_count += 1
                # update combined_map to avoid repeating this creation
                combined_map[url] = {'record': c, 'articles': [art_url]}
            elif art_url not in combined_map[url]['articles']:
                # update a non-down record
                combine(o, existing=combined_map[url]['record'])
                # avoid repeat
                combined_map[url]['articles'].append(art_url)
                print 'Updating non-download record: %s.' % url

    disco_file.close()

    # read the downloaded file info, find its corresponding discovery
    # info and combine the two
    down_file = open(args['DOWN'], 'r')
    for line in down_file:
        down = json.loads(line)
        url = down['url']
        if url not in discovered_map:
            # well this is unexpected
            print('Downloaded file is not discovered? Are you mad? %s'
                                                                % url)
            continue

        c = None
        for art, disco in discovered_map[url].iteritems():
            if url in combined_map:
                c = combined_map[url]['record']
                if art in combined_map[url]['articles']:
                    continue
                combine(disco, down, existing=c)
                combined_map[url]['articles'].append(art)
                print 'Updating record: %s.' % url
            else:
                c = combine(disco, down, existing=c)
                combined_map[url] = {'record': c, 'articles': [art]}
                combined_count += 1

    down_file.close()

    # open out_file for writing and empty it
    out_file = open(args['COMBI'], 'w')
    out_file.seek(0)
    out_file.truncate()

    # extract the combined records from combined_map, sort and dump
    json.dump(sorted([ x['record'] for x in combined_map.itervalues()],
                     key=lambda x: (x['pubdate'],
                                    x['url'] or x['presentation_url'])
                    ), out_file, indent=4, separators=(',', ': '))

    out_file.close()

    print 'Total records written: %d. New records: %d' % (
                                  len(combined_map), combined_count)

    return 0


if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.0.1')
    sys.exit(main(arguments))

