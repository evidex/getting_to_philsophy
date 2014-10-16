"""

"""
from __future__ import print_function
from __future__ import division
import sys
import time
import pygraphviz as pgv
import argparse
import urllib2
from bs4 import BeautifulSoup, SoupStrainer, Tag, NavigableString

class getting_to_philosophy:
    def __init__(self):
        """
            Define filters for HTML on the page.
        """
        self.div_id = "mw-content-text" # the division in the page we'll look for links in
        self.content_tags = ['p', 'ul', 'ol'] # the tags (w/in div) we will look for links w/in


    def get_philosophy_link(self, url):
        """
             Get a GTP link from this page.
             Return that link.
             Return False on a bad url or no links available.
        """
        self.set_page(url)
        self.page_name = return_wiki_page_name(url)

        # url could not be followed or bad wiki page
        if self.page == False or self.page_name == False:
            return False

        self.soup = self.set_parser()
        return self.philosophy_link()


    def set_page(self,url):
        """
            Follow a url, and set self.page
        """
        self.url = url
        self.page = follow_url(self.url)


    def set_parser(self):
        """
            Set our parser to the div we're interested in
        """
        strained = SoupStrainer('div', id=self.div_id)
        return BeautifulSoup(self.page, parse_only=strained)


    def seek_to_first_paragraph(self):
        # start our search for link at the first paragraph under self.div_id
        first_link_containing_element = self.soup.find('p')

        # if the paragraph is in a table, skip it (this was breaking the /Human page...)
        while is_in_table(first_link_containing_element):
            first_link_containing_element = first_link_containing_element.find_next('p')

        # if there's no first paragraph, then broaden search to include all our content tags
        if first_link_containing_element == None:
            first_link_containing_element = soup.find(self.content_tags)

        return first_link_containing_element


    def philosophy_link(self):
        """
            Get the first link on this page that satisfies
            the GTP criteria (not in parens,
            not italicized, not red, not the same page).

            Return the full http://en.wikipedia.org/wiki/... link
            Return False if no such link exists.
        """
        current_page_element = self.seek_to_first_paragraph()

        while current_page_element != None:
            no_parenthesized_links = remove_parenthesized_links(current_page_element)
            all_links = no_parenthesized_links.find_all('a')
            for link in all_links:
                if link['href'].startswith("/wiki/"):
                    full_link = "http://en.wikipedia.org" + link['href']
                    is_wiki = is_wiki_url(full_link)
                    is_special = is_special_wiki_page(full_link) # check if the page is a Help page, File page,...
                    is_same_page = return_wiki_page_name(full_link) == self.page_name
                    italicized = is_italicized(link)
                    if is_wiki and not is_special and not italicized and not is_same_page:
                        return full_link

            current_page_element = current_page_element.find_next(self.content_tags)

        return False




def remove_parenthesized_links(tag):
    """
        Given a BeautifulSoup Tag, look through its children
        and remove any anchor elements that are inside parentheses.
        Return a new Beautiful soup representation of this section.
    """
    without_parens = []
    in_parens = False

    # each HTML tag will be in an individual cell
    # Eg: ['<a href="http://example.com/">', 'I linked to a page', '</a>']
    subtree_list = tag_subtree_as_list(tag)

    in_anchor = False
    in_parens = False
    for element in subtree_list:
        in_tag = False
        if element.startswith("<"):
            in_tag = True
            if element.startswith("<a"):
                in_anchor = True
            elif element.startswith("</a>"):
                in_anchor = False

        # don't look for parens in any type of tag element
        if not in_tag:
            for char in element:
                if char == "(":
                    in_parens = True
                elif char == ")":
                    in_parens = False

        # append this element if it's not an anchor, or if it's an anchor
        # that's not in parens
        if (not in_anchor or (in_anchor and not in_parens)):
            without_parens.append(element)

    return BeautifulSoup("".join(without_parens))



def tag_subtree_as_list(tag):
    """
        Given a tag, return a list of its subtree with each
        HTML tag in its own cell.
        Eg: ['<a href="http://example.com/">', 'I linked to a page', '</a>']
    """

    # unicode string w/ each tag on its own line
    pretty = tag.prettify()

    # make each line a cell in pretty_list
    pretty_list = []
    for element in pretty.splitlines():
        pretty_list.append(element.lstrip())

    return pretty_list




def is_italicized(tag):
    """
        Given a BeautifulSoup Tag, return True if its
        immediate parent is italicized. Return False o.w.
    """
    return tag.find_parent().name == "i"


def is_in_table(tag):
    """
        Return True if a Beautiful Soup Tag is w/in a table.
        False o.w.
    """
    for parent in tag.parents:
        if parent.name == 'td' or parent.name == 'tr' or parent.name == 'table':
            return True
    return False


def is_special_wiki_page(url):
    """
        Return True is a wiki url is a help page,
        or a file page, or a special page...
    """
    is_red = is_red_link(url)
    is_help = is_help_page(url)
    is_special = is_special_page(url)
    is_file = is_file_page(url)
    return (is_red or is_help or is_special or is_file)


def is_red_link(url):
    """
        Quick test to determine if a url is a "red" link on wikipedia.
    """
    if "redlink=1" in url:
        return True
    return False

def is_help_page(url):
    """
        Quick test to determine if url is a Wiki help page
    """
    if "Help:" in url:
        return True
    return False

def is_special_page(url):
    """
        Quick test for a special page on wiki
    """
    if "Special:" in url:
        return True
    return False

def is_file_page(url):
    """
        Quick test to exclude Wikipedia files
    """
    if "File:" in url:
        return True
    return False



def is_wiki_url(url):
    """
        Return True if 'url' is a URL to a page on English wikipedia.
        Return False otherwise.
    """
    valid_http_start = url.startswith("http://en.wikipedia.org/wiki/")
    valid_https_start = url.startswith("https://en.wikipedia.org/wiki/")
    if valid_http_start or valid_https_start:
        return True
    return False



def return_wiki_page_name(wiki_url):
    """
        Given a wiki URL, return the name of that page.
        Returns False if 'wiki_url' is not a wiki page.
    """
    if is_wiki_url(wiki_url):
        url_split = wiki_url.split("/wiki/")
        page_name = url_split[1]
        return page_name
    return False




def follow_url(url):
    """
        Return the page at the given URL.
        Return False and print the exception if the URL is
        not valid/followable.
    """
    try:
        assert is_wiki_url(url)
        page = urllib2.urlopen(url)
        return page
    except (ValueError, urllib2.URLError) as e:
        print( e )
        return False



def hop_to_wiki_url(graph, start_wiki_url, destination_wiki_url, limit):
    """
        Following the rules of Getting to Philosophy, hop from
        a start wiki url, to a destination url.  Output the links on
        the path and # hops.
        'limit' caps the # of pages we can visit before giving up.
    """
    start_page_name = return_wiki_page_name(start_wiki_url)
    end_page_name = return_wiki_page_name(destination_wiki_url)
    print( "Finding path from {} to {}".format(start_page_name, end_page_name) )
    edges = []

    # handle the case that we start at our destination
    if start_page_name == end_page_name:
        return None

    # create our philosophy_link fetching object
    philosophy_links = getting_to_philosophy()

    # grab our first url
    next_url = philosophy_links.get_philosophy_link(start_wiki_url)
    page_name = start_page_name

    data = {
        "page_name": page_name,
        "found_shortcut": False,
        "failed": False,
        "hops": 0}
    while next_url != False and data["hops"] < limit:
        prev_page_name = page_name
        page_name = return_wiki_page_name(next_url)
        edges.append((prev_page_name, page_name))
        print('.', end='')
        data["hops"] += 1

        # Check for a goal condition
        data["found_shortcut"] = graph.has_node(page_name)
        if page_name == end_page_name or data["found_shortcut"]:
            print("X  -  {} hops".format(data["hops"]), end="")
            # Add the edges to overall graph
            graph.add_edges_from(edges)
            if data["found_shortcut"]:
                data["found_shortcut"] = True
                print(" Found existing path from {} to {}".format(page_name, end_page_name))
            print("")
            return data
        # Didn't find a goal condition, get next url and keep going
        next_url = philosophy_links.get_philosophy_link(next_url)

    # Couldn't reach end_url
    print("#  -  Couldn't reach {}".format(end_page_name))
    data["failed"] = True
    return data


def run(num_runs, output_filename, end_url):
    # Create a graph
    graph = pgv.AGraph(directed=True)
    random_url_gen = "http://en.wikipedia.org/wiki/Special:Random"
    limit = 50
    results = []
    print("\nAttempting to get to {} from {} random Wikipedia pages. Hop limit --> {}".format(return_wiki_page_name(end_url), num_runs, limit))
    # For some random pages
    start_time = time.time()
    for i in xrange(num_runs):
        print("{}: ".format(i), end="")
        # Get random url
        start_url = follow_url(random_url_gen).geturl()
        # Populate graph with path form start_url to end_url
        try:
            data = hop_to_wiki_url(graph, start_url, end_url, limit)
            results.append(data)
        except:
            print(sys.exc_info())
            print("We broke something")
            pass
    time_taken = time.time() - start_time
    time_taken_minutes = round(time_taken/60)
    # Draw resulting graph
    print("Drawing graph to {}".format(output_filename))
    graph.layout(prog="dot")
    graph.draw(output_filename)
    # print(results)
    total_runs = len(results)
    num_pages_visited = graph.number_of_edges()
    avghops = 0
    num_failed = 0
    for data in results:
        if not data["found_shortcut"]:
            avghops += data["hops"]
        if data["failed"]:
            failed += 1
    stats = """
    Total number of runs                    --> {}
    Runs with no path to end point          --> {}
    Average number of hops (no shortcuts)   --> {}
    Number of pages visited                 --> {}
    Time taken (minutes)                    --> {}
    """.format(total_runs, num_failed, avghops, num_pages_visited, time_taken_minutes)
    with open("stats.txt", "rt") as f:
        f.write(stats)
    print(stats)


################
# "Main":
################
if __name__ == "__main__":
    # build command-line parser
    parser = argparse.ArgumentParser(description='Generates a graph of the path from a number of random Wikipedia pages back to philosophy')
    parser.add_argument('--NUMBER_OF_PAGES', '-n', help='Number of random pages to add to the graph', default=10, type=int )
    parser.add_argument('--OUTPUT_FILENAME', '-o', help="Name of output file to generate", default="output_graph.png")
    parser.add_argument('--END_URL', '-e', default="https://en.wikipedia.org/wiki/Philosophy")

    # parse command line arguments
    args = parser.parse_args()

    run(args.NUMBER_OF_PAGES, args.OUTPUT_FILENAME, args.END_URL)
