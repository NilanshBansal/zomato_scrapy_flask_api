from flask import Flask,jsonify,request,render_template
from allReviews import AllreviewsSpider
import json
from scrapy.crawler import CrawlerRunner

app = Flask(__name__)
crawl_runner = CrawlerRunner()      # requires the Twisted reactor to run

reviews_list = []                    # store quotes
scrape_in_progress = False
scrape_complete = False

@app.route('/crawl')
def crawl():
    global scrape_in_progress
    global scrape_complete
    location = request.args.get("location")


    if not scrape_in_progress:
        scrape_in_progress = True
        global reviews_list
        eventual = crawl_runner.crawl(AllreviewsSpider , location=location, reviews_list=reviews_list)
        eventual.addCallback(finished_scrape)
        return 'SCRAPING'
    elif scrape_complete:
        return 'SCRAPE COMPLETE'
    return 'SCRAPE IN PROGRESS'


@app.route('/results')
def get_results():
    global scrape_complete
    if scrape_complete:
        return json.dumps(reviews_list)
    return 'Scrape Still Progress'

def finished_scrape(null):
    global scrape_complete
    scrape_complete = True


if __name__=='__main__':
    from sys import stdout

    from twisted.logger import globalLogBeginner, textFileLogObserver
    from twisted.web import server, wsgi
    from twisted.internet import endpoints,reactor

    globalLogBeginner.beginLoggingTo([textFileLogObserver(stdout)])

    root_resource = wsgi.WSGIResource(reactor, reactor.getThreadPool(), app)
    factory = server.Site(root_resource)
    http_server = endpoints.TCP4ServerEndpoint(reactor, 9000)
    http_server.listen(factory)

    reactor.run()






# app.run(port=5000)

