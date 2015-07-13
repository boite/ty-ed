# Methodologies

## Manual review of EFF and CF lists

### Crawl CF and EFF, saving to json lines files:-

    $ cd scrape/docinfo/
    $ scrapy crawl --output-format=jsonlines \
                   --output=../../data/cf.jsonl \
                   --logfile=../../data/cf.log \
                   cf
    $ scrapy crawl --output-format=jsonlines \
                   --output=../../data/eff.jsonl \
                   --logfile=../../data/eff.log \
                   eff

### Review the URLs scraped from CF and EFF:-

    $ cd data/
    $ python ../script/source-discover.py -s discovery.state \
                                          -i cf.jsonl -i eff.jsonl \
                                          discovered.jsonl

The idea here is that the tool outputs a URL for examination by a
human and prompts for the number of primary sources to create.  For
example, there may be just one primary source revealed in the article
under review, or there may be 40+.  After inputting this number, the
human is prompted to enter the following information for each primary
source:-

- Publication date: of the primary source; YYYY-MM-DD.
- Presentation url: This is the URL of the page where the primary
  source can be viewed directly. It may be the same as the article
  under review where the primary source is an embedded image, or it
  may be a separate page in which the primary source is embedded. It
  may also be left empty, for example if the article under review only
  provides a link to download the primary source.
- Primary source url: the URL of the primary source itself. This also
  may be empty if the primary source is not downloadable, e.g. where
  the article under review presents the text of the primary source,
- Accompanying article url: this is often, but not always the url of
  the article under review.
- Accompanying article date: publication date as displayed in the
  accompanying article; YYYY-MM-DD.

The tool attempts to make this input process quicker by providing a
default value for some of the inputs so that the human need only
press enter except where the value needs to be changed.

The output file is json lines with a line per discovered primary
source.


### Get a list of URLs from r/NSALeaks timeline wiki

- Head to r/NSALeaks, scroll to the bottom of the wiki page and click
  'view source'.
- Copy the wiki source into a file in data/.
- Repeat for all continuance wiki pages.
- Generate a list of urls (see commands, below)

Generate a list of urls from the wiki markup:-

    $ cd data/
    $ python ../script/r-nsaleaks-wiki2list.py 1.wiki >> timeline.list
    $ python ../script/r-nsaleaks-wiki2list.py 2.wiki >> timeline.list


### Review the URLs from r/NSALeaks timeline wiki

    $ cd data
    $ python ../script/source-discover.py -s discovery.state \
                                          -f url -i timeline.list \
                                          discovered.jsonl


[r/NSALeaks]: https://www.reddit.com/r/NSALeaks/wiki/timeline
              "r/NSALeaks Timeline"


## Retrieval of Primary Sources

Each file, once downloaded, should be named uniquely while having the
following name components:-

- A date, leading the file name, so that it falls naturally into date order.
- The original file name.
- A file extension to assist with selection of an application with
  which to view the file

The primary sources were not named consistently by the publishers and
do not follow the desired naming scheme.  Downloaded files will be
renamed according to the following rules:

- Each component of the file name is separated with an underscore
  character.
- The name begins with the date of publication of the Primary Source
  in the format `YYYY-MM-DD` where Y, M and D are numeric characters.
- A SHA256 digest is made over the content of the file and the first
  8 hexadecimal characters is the next component of the file name.
  This provides a strong assurance that the resulting name is unique.
- The original file name is the next component of the file name.

In addition to these rules, a file name extension is appended to the
file name if the original name of the file does not include one.

### Download and store the discovered Primary Sources

    $ python script/down.py --input=data/discovered.jsonl
                            --output=data/downloaded.jsonl
                            dox/

This will place the downloaded files in `dox/` and write an entry for
each file into `data/downloaded.jsonl`.  Each entry is a json line
containing the following information:

- url: The URL from which the file was retrieved.
- filename: The name of the file on disk.
- original_filename: The original name of the file.
- digest: The SHA256 digest of the content of the file.


## Primary Source Catalogue creation

Cataloguing the Primary Sources is now a simple matter of combining
information from the discovery and retrieval steps:-

    $ cd data
    $ python ../script/catalogue.py --include catalogue_manpopd.json
                                    discovered.jsonl
                                    downloaded.jsonl
                                    catalogue.json

Each item in [data/catalogue.json](../data/catalogue.json) is an
object, in json notation:-

    {
        pubdate: '',
        url: '',
        presentation_url: '',
        published_files: [
            {
                file: {
                    digest: '',
                    name: '',
                    original_name: '',
                    files: []
                },
                index_type: '',
                index: ''
            }
        ],
        alternative_files: [],
        accompanying_articles: [
            {
                pubdate: '',
                url: ''
            }
        ]
    }

