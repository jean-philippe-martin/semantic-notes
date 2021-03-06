"""Web server, to show the pages you design.

Pass the file to serve as a command-line argument.

Example:

pyhon web.py samples/table.txt

Currently serving:

/ : index
/get/ : list of pages
/get/page_name : shows the specified page
"""
import webapp2
import interpret
from paste import httpserver
from paste.urlparser import StaticURLParser
from paste.fileapp import DirectoryApp
from paste.cascade import Cascade
from markupsafe import Markup
import sys
import os
from kb import unlist
import people



class Hello(webapp2.RequestHandler):
    def get(self):
        self.response.write('<br/><a href="get/">List of pages</a>')


class Static(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-type']="text/css"
        self.response.write("""
.lightonhover:hover {
    background-color: yellow;
}
""")


# Load the data
pages=None
kb=None


def load(fnames):
    global pages
    global kb
    pages,kb=interpret.files(fnames)
    # apply "people" rules
    people.fixup(kb)


def linkify(word):
    if word in pages or word in kb:
        return Markup('<a href="{0}">{0}</a>\n').format(word)
    return word

class Get(webapp2.RequestHandler):
    def get(self, page=None):
        key = kb.normalize_page(page)
        if key and key in pages or page in kb:
            self.response.write(Markup('<h1>{0}</h1>\n').format(page))
            boom = None
            if key in pages: 
                boom=pages[key]
                # an attempt to make sure images don't bring in a scrollbar... doesn't work though.
                self.response.write('<div width="100%">\n')
                self.response.write(boom.html())
                self.response.write('</div>\n')
            ks = set(kb.get(page, {}).keys())
            if boom: ks -= set(boom.kb().keys())
            if ks:
                self.response.write('<ul>\n')
                for k in ks:
                    self.response.write(Markup('<li>{0}: ').format(k))
                    #for kx in kb[page][k]:
                    #    self.response.write(linkify(str(kx)) + ' ')
                    self.response.write(', '.join(linkify(str(kx)) for kx in kb[page][k]))
                    self.response.write(Markup('</li>\n'))

                self.response.write('</ul>\n')
        else:
            # show an index
            self.response.write('<ul>\n')
            for k in sorted(pages.keys(), key=lambda f: f.upper()):
                self.response.write(Markup('<li><a href="{0}">{0}</a></li>\n').format(k))
            self.response.write('</ul>\n')


def main():
    if len(sys.argv)<2:
        print 'Usage:'
        print 'python web.py <file names>'
        return
    fname = sys.argv[1]
    load(sys.argv[1:])
    app = webapp2.WSGIApplication([
        ('/', Hello),
        ('/get/(.*)', Get),
        #('/static/web.css', Static)
    ], debug=True)
    static_media_server = StaticURLParser("static/")
    app = Cascade([static_media_server, app])
    httpserver.serve(app, host='127.0.0.1', port='8080')


if __name__ == '__main__':
    main()