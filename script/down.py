#  down.py Slowly download files of discovered primary sources.
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
Download files identified in a jsonl of discovered primary sources.

Usage:
    down.py (-i SOURCE | --input=SOURCE) (-o META | --output=META)
            DESTINATION_DIR
    down.py (-h | --help)
    down.py --version

Arguments:
    DESTINATION_DIR  Destination directory for downloaded files.

Options:
    -i SOURCE --input=SOURCE  Path to jsonl of discovered primary
                              sources.
    -o META --output=META     Path to write a jsonl of downloaded file
                              metadata.
    -h --help                 Show this screen.
    --version                 Show version.

"""

from docopt import docopt
from urlparse import urlsplit
from collections import Counter
import os, sys, json, urllib2, hashlib, mimetypes, imghdr


REMOTE_FILE_READLEN = 8192
HTTP_USER_AGENT = 'Thank you Ed (https://github.com/boite/ty-ed)'


def download(target, destdir, log_file):
    '''Retrieve a remote file, save it to destdir and catalogue it.

    Files are saved with the following filename pattern:-

        <pubdate>_<digest[:8]>_<original_filename>[.<ext>]

    Where:-
      - pubdate is as supplied in target['pubdate']
      - digest[:8] is first 8 hex chars of the sha256 of the content
      - original_filename is the original filename as in target['url']
      - ext is a guessed file extension for files not having one

    A json line, having the following keys, is appended to log_file:-
      - url: the download url
      - filename: the aforementioned filename
      - original_filename: the original filename
      - digest: sha256 of the content, as hex chars
    '''

    req = urllib2.Request(target['url'],
                          headers={'user-agent': HTTP_USER_AGENT })
    try:
        u = urllib2.urlopen(req)
    except IOError, e:
        print '%s trying to open %s' % (target['url'], str(e))
        return False
    try:
        content = get_remote_content(u)
    except IOError, e:
        print '%s trying to read %s' % (target['url'], str(e))
        return False

    hash_func = hashlib.sha256() 
    hash_func.update(content) 
    # meta
    digest = hash_func.hexdigest()
    del hash_func
    # meta
    original_name = urlsplit(target['url']).path.split('/')[-1]
    # meta
    fs_extension = get_missing_extension(content, original_name, u.info())
    fs_name = make_filename([target['pubdate'], digest[:8]],
                        original_name, fs_extension)

    try:
        persist_file(content, destdir, fs_name)
    except IOError, e:
        print e
        return False
    
    meta = {'url': target['url'], 'filename': fs_name,
            'original_name': original_name, 'digest': digest}
    log_file.write(json.dumps(meta))
    log_file.write('\n')

    return True


def make_filename(name_parts, original_name, extension):
    name_parts.append(original_name)
    name = '_'.join(name_parts)
    if extension:
        name += extension
    return name


def get_missing_extension(content, original_name, mime_msg):
    '''Attempt to provide a file extension for a file without one.'''

    # has the file got an extension?
    original_parts = original_name.rpartition('.')
    if original_parts[1] and original_parts[2]:
        return None

    # is the file an image?
    candidate_ext = imghdr.what(None, content)
    if candidate_ext:
        return '.' + candidate_ext

    # is there a hint from an HTTP Content-Type header?
    if not mime_msg.getheader('content-type'):
        return None
    mimetype = mime_msg.gettype()
    all_extensions = mimetypes.guess_all_extensions(mimetype)
    if not all_extensions:
        print('Unknown Content-Type %s. '
              'Cannot guess an extension for file %s.' %
              (mimetype, original_name))
        return None

    prefs = {
        'image/jpeg': 'jpeg',
    }
    return mimetype in prefs and prefs[mimetype] or all_extensions[0]


def persist_file(content, path, name):
    fname = os.path.join(path, name)
    if os.path.isfile(fname):
        return
    f = open(fname, 'wb')
    f.write(content)
    f.close()


def get_remote_content(remote_file):
    content = ''
    while True:
        buf = remote_file.read(REMOTE_FILE_READLEN)
        if not buf:
            break
        content += buf
    return content


def get_remote_info(path):
    '''Read the supplied input file and return a list of url and
    pubdate pairs.
    '''
    info = []
    f = open(path, 'r')
    print 'Reading input file: %s' % path
    for line in f:
        j = json.loads(line)
        if j['url'] != '':
            info.append({k: j[k] for k in ['url', 'pubdate']})
    f.close()
    return info


def get_prev_state(path):
    '''Read the supplied output file from a previous invocation and
    return a dict containing previously downloaded url as keys.
    '''
    info_map = {}
    try:
        f = open(path, 'r')
    except IOError, e:
        pass
    else:
        print 'Reading output file: %s' % path
        for line in f:
            j = json.loads(line)
            info_map[j['url']] = True
        f.close()
    return info_map


def map_remote_info_by_host(remote_info):
    '''Map the supplied list of url and pubdate pairs by host name.'''
    hmap = {}
    for remote in remote_info:
        h = urlsplit(remote['url']).netloc
        if h not in hmap:
            hmap[h] = []
        hmap[h].append(remote)
    return hmap


def shuffle_remote_info(remote_info):
    '''Rearrange a list of url and pubdate pairs to minimise
    consecutive downloads from the same host.
    '''
    shuffled = []
    by_host = map_remote_info_by_host(remote_info)
    c = Counter({k: len(v) for k, v in by_host.iteritems()})
    last = None
    while True:
        most_common = c.most_common(2)
        candidate_keys = [k for k, count in most_common if count]
        if not candidate_keys:
            break
        if candidate_keys[0] == last:
            candidate_keys.reverse()
        chosen_key = candidate_keys[0]
        shuffled.append(by_host[chosen_key].pop())
        c[chosen_key] -= 1
        last = chosen_key
    return shuffled


def main(args):
    '''Download, persist and catalogue a list of remote files.'''

    prev_state = get_prev_state(args['--output'])
    remotes = shuffle_remote_info(
        [r for r in get_remote_info(args['--input'])
                 if r['url'] not in prev_state])

    if len(prev_state):
        print '%d files were previously downloaded.' % len(prev_state)

    if len(remotes):
        try:
            out_file = open(args['--output'], 'a')
        except IOError, e:
            print 'Cannot open output file for appending: %s' % e
            return 1

        print 'Downloading a maximum of %d files.' % len(remotes)

        for idx, r in enumerate(remotes, start=1):
            if r['url'] in prev_state:
                continue
            try:
                success = download(r, args['DESTINATION_DIR'], out_file)
            except KeyboardInterrupt, e:
                print 'Quitting!'
                out_file.close()
                return 0
            else:
                prev_state[r['url']] = success

            sys.stdout.write(success and '.' or '!')

        out_file.close()
        print '\nFin!'
    else:
        print 'Nothing to do!'

    return 0


if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.0.1')
    sys.exit(main(arguments))

