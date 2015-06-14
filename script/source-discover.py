#  source-discover.py  Discover Ed Snowden Primary Source documents.
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
Manually review URLs to discover and record primary source documents
and accompanying reporting.

Usage:
    source-discover.py [-f FORMAT | --input-format=FORMAT]
                       (-s SFILE  | --state=SFILE)
                       (-i INFILE | --input INFILE ...) OUTFILE
    source-discover.py (-h | --help)
    source-discover.py --version

Arguments:
    OUTFILE  Append jsonl to this file.

Options:
    -f FORMAT --input-format=FORMAT  Format of INFILE, either "item"
                                     or "url" [default: item]
    -s SFILE --state=SFILE           A list of URLs which have already
                                     been reviewed.
    -i INFILE --input INFILE         Input file(s) of either scrapy
                                     items in jsonl format or a list
                                     or URLs.
    -h --help                        Show this screen.
    --version                        Show version.

"""

from docopt import docopt
import sys, json, datetime

INPUT_FORMAT_URL = 'url'

def main(args):

    state_file = None
    out_file = None

    # sorted list of input
    items = []
    # list of reviewed urls
    state = {}
    # map of partially reviewed urls to saved primary source urls
    partials = {}

    # process a state file which lists (possible) article URLs which
    # have already been reviewed
    try:
        f = open(args['--state'], 'r')
    except IOError:
        pass
    else:
        print 'Reading state file: %s' % args['--state']
        for line in f:
            state[line.strip()] = True
        f.close()
    # now open the state file for appending
    try:
        state_file = open(args['--state'], 'a')
    except IOError, e:
        print 'Cannot open state file for appending: %s' % e
        return 1

    # map partially reviewed items to saved primary source urls
    try:
        f = open(args['OUTFILE'], 'r')
    except IOError, e:
        pass
    else:
        print 'Reading output file: %s' % args['OUTFILE']
        for line in f:
            ps = json.loads(line)
            k = ps.get('skey')
            if k is None or k in state:
                continue
            if k not in partials:
                partials[k] = []
            partials[k].append(ps.get('url'))
        f.close()
    # now open the output file for appending
    try:
        out_file = open(args['OUTFILE'], 'a')
    except IOError, e:
        print 'Cannot open output file for appending: %s' % e
        return 1

    # load the items and sort by ascending pubdate
    for fname in args['--input']:
        f = open(fname, 'r')
        print 'Reading input file: %s' % fname
        if args['--input-format'] == INPUT_FORMAT_URL:
            for line in f:
                items.append(line.strip())
        else:
            for line in f:
                items.append(json.loads(line))
            items.sort(key = lambda x: datetime.datetime.strptime(
                                    x.get('pubdate', '2020-01-01'),
                                                       '%Y-%m-%d'))
        f.close()

    # get the next item to review
    progress_counter = 0
    for item in items:
        if args['--input-format'] == INPUT_FORMAT_URL:
            url = item
            date = ''
        else:
            url = item.get('publisher_url', '')
            date = item.get('pubdate', '')
        if url == '' or url in state:
            progress_counter += 1
            continue
        # review the URL
        progress_counter +=1
        print('\nItem %d of %d.' % (progress_counter, len(items)))
        if review_item(url, date, out_file, partials.get(url, [])):
            state_file.write(url)
            state_file.write('\n')
            state[url] = True
        should_continue = raw_input('\nContinue with next item? y/n [y] ') or 'y'
        if should_continue != 'y':
            break

    state_file.close()
    out_file.close()
    return 0

def review_item(url, date, appendfile, previously_saved):
    '''Present a URL and facillitate the input of primary source info.

    The URL should be reviewed and the number of primary source
    documents published there determined (this may be zero).  Then
    details about each primary source should be input and will be
    written to the supplied appendfile.  Ctrl-c aborts the input
    process and exits this function without further writes to the
    appendfile.
    '''

    review_completed = False
    written = 0
    print url

    try:
        # how many primary sources will we create from this url
        num_ps = raw_input('Number of Primary Sources to create? [1] ') or '1'
        if len(previously_saved):
            print 'Previously saved:'
        for ps in previously_saved:
            print ps

        common_pubdate = False
        common_art_url = False
        common_art_pubdate = False
        common_pres_url = ''
        for i in range(len(previously_saved), int(num_ps)):
            print 'Primary Source #%d of %s:' % (i+1, num_ps)

            pubdate = raw_input('Publication date (%%Y-%%m-%%d)? [%s] '
                                % (common_pubdate or date)
                               ) or common_pubdate or date
            presentation_url = raw_input('Presentation url? [%s] '
                                         % common_pres_url
                                        ) or common_pres_url
            doc_url = raw_input('Primary Source url? ')
            article_url = raw_input('Accompanying article url? [%s] '
                                    % (common_art_url or url)
                                   ) or common_art_url or url
            article_pubdate = raw_input('Accompanying article date (%%Y-%%m-%%d)? [%s] '
                                    % (common_art_pubdate or pubdate)
                                   ) or common_art_pubdate or pubdate

            # write the primary source
            ps = {'url': doc_url, 'presentation_url': presentation_url,
                  'pubdate': pubdate, 'article_url': article_url,
                  'article_pubdate': article_pubdate, 'skey': url}
            appendfile.write(json.dumps(ps))
            appendfile.write('\n')
            written += 1

            # a non-empty presentation_url might be the same for all
            # of the following Primary Sources
            if presentation_url != '':
                common_pres_url = presentation_url

            # a non-empty article_pubdate might be the same for all
            # of the following Primary Sources
            if ((not common_art_pubdate and pubdate != article_pubdate)
                or (common_art_pubdate and common_art_pubdate != article_pubdate)):
                common_art_pubdate = article_pubdate

            # a pubdate that isn't date might be the same for all of
            # the following Primary Sources
            if ((not common_pubdate and date != pubdate)
                or (common_pubdate and common_pubdate != pubdate)):
                common_pubdate = pubdate

            # an article_url that isn't url might be the same for all
            # of the following Primary Sources
            if ((not common_art_url and url != article_url)
                or (common_art_url and common_art_url != article_url)):
                common_art_url = article_url

    except KeyboardInterrupt:
        print '\nAborting this item.'
        review_completed = False
    else:
        review_completed = True
    finally:
        print 'Written %d Primary Source entries.' % written

    return review_completed == True

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.0.1')
    sys.exit(main(arguments))

