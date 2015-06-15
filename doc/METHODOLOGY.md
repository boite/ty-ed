# Methodologies

## Manual review of EFF and CF lists

### Crawl CF and EFF, saving to json lines files:-

    $ pushd scrape/docinfo/
    $ scrapy crawl --output-format=jsonlines \
                   --output=../../data/cf.jsonl \
                   --logfile=../../data/cf.log \
                   cf
    $ scrapy crawl --output-format=jsonlines \
                   --output=../../data/eff.jsonl \
                   --logfile=../../data/eff.log \
                   eff
    $ popd

### Review the URLs scraped from CF and EFF:-

    $ pushd data/
    $ python ../script/source-discover.py -s discovery.state \
                                          -i cf.jsonl -i eff.jsonl \
                                          discovered.jsonl
    $ popd

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
  may be a separate page in whcih the primary source is embedded. It
  may also be left empty, for example if the article under review only
  provides a link to download the primary source.
- Primary source url: the URL of the primary source itself. This also
  may be empty if the primary source isn't downloadable, e.g. where
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
- Generate a list of urls:-

    $ pushd data/
    $ python ../script/r-nsaleaks-wiki2list.py 1.wiki >> timeline.list
    $ python ../script/r-nsaleaks-wiki2list.py 2.wiki >> timeline.list
    $ popd


### Review the URLs from r/NSALeaks timeline wiki

    $ pushd data/
    $ python ../script/source-discover.py -s discovery.state \
                                          -f url -i timeline.list \
                                          discovered.jsonl
    $ popd


[r/NSALeaks]: https://www.reddit.com/r/NSALeaks/wiki/timeline
              "r/NSALeaks Timeline"
