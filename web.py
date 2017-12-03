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
from markupsafe import Markup
import sys
from kb import unlist



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


def load(fname):
    global pages
    global kb
    pages,kb=interpret.file(fname)


def linkify(word):
    if word in pages or word in kb:
        return Markup('<a href="{0}">{0}</a></li>\n').format(word)
    return word

class Get(webapp2.RequestHandler):
    def get(self, page=None):
        if page and page in pages or page in kb:
            self.response.write(Markup('<h1>{0}</h1>\n').format(page))
            boom = None
            if page in pages: 
                boom=pages[page]
                self.response.write(boom.html())
            ks = set(kb.get(page, {}).keys())
            if boom: ks -= set(boom.kb().keys())
            if ks:
                self.response.write('<ul>\n')
                for k in ks:
                    self.response.write(Markup('<li>{0}: {1}</li>\n').format(k, linkify(unlist(kb[page][k]))))
                self.response.write('</ul>\n')
        else:
            # show an index
            self.response.write('<ul>\n')
            for k in pages.keys():
                self.response.write(Markup('<li><a href="{0}">{0}</a></li>\n').format(k))
            self.response.write('</ul>\n')


def main():
    if len(sys.argv)<2:
        print 'Usage:'
        print 'python web.py <file name>'
        return
    fname = sys.argv[1]
    load(sys.argv[1])
    app = webapp2.WSGIApplication([
        ('/', Hello),
        ('/get/(.*)', Get),
        ('/static/web.css', Static)
    ], debug=True)
    #static_media_server = webapp2.DirectoryApp("/static")
    #app = Cascade([static_media_server, app])
    httpserver.serve(app, host='127.0.0.1', port='8080')


if __name__ == '__main__':
    main()