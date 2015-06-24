import csv, re, cStringIO, codecs

from pattern.web import abs, URL, DOM, plaintext, strip_between
from pattern.web import NODE, TEXT, COMMENT, ELEMENT, DOCUMENT

#unicode writer
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# Getting data
page = 0
while page != 5:

    # Creating the csv output file for writing into as well as defining the writer
    output = open("NL" + str(page) + ".csv", "wb")
    writer = UnicodeWriter(output)

    # Make Header
    writer.writerow(["Name", "Genre", "Location", "Status", "Years Active", "Albums"])

    # Visits the first list
    baseUrl = "http://www.metal-archives.com/browse/ajax-country/c/NL/json/1?sEcho=1"
    url = URL(baseUrl + "&iDisplayStart=" + str(page * 500))
    if url.exists:
        dom = DOM(url.download(cached=True))

        # Get Name, Country, Subgenres, Status
        for e in range(1, len(dom) - 1, 4):
            Name = dom[e].content
            BandID = dom[e].attrs["href"].split("/")

            LocationAndGenre = unicode(dom[e + 1]).split(",")
            Genre = LocationAndGenre[1].replace("\"", "").replace(",", "-").strip()
            Location = LocationAndGenre[2].replace("\"", "").replace(",", "-").strip()
            Status = dom[e + 2].content.replace("\"", "").strip()
            YearsActive = ""
            Albums = ""

            # Go to band page
            link = URL(dom[e].attrs["href"])
            if link.exists:
                BandPage = DOM(link.download(cached=True))

                YearsActive = BandPage.by_id("wrapper").by_id("content_wrapper").by_id("band_content").by_id("band_info").by_id("band_stats").by_tag("dl")[2].by_tag("dd")[0].content
                YearsActive = YearsActive.split(",")
                years = ""
                for e in range(0, len(YearsActive)):
                    # Deletes all html tags in yearsactive
                    YearsActive[e] = YearsActive[e].replace(r'<([A-Z][A-Z0-9]*)\b[^>]*>(.*?)</\1>', '')
                    YearsActive[e] = YearsActive[e].replace("\"", "").strip()
                    YearsActive[e] = YearsActive[e].replace("\t", "").replace("   ", "")
                    if(len(YearsActive) > 1 and e < (len(YearsActive) - 1)):
                        years += YearsActive[e] + ", "
                    else:
                        years += YearsActive[e]
                
                YearsActive = "".join(years)
                # print YearsActive

            # Go to band discography
            link = URL("http://www.metal-archives.com/band/discography/id/" + BandID[5] + "/tab/all")
            if link.exists:
                AlbumPage = DOM(link.download(cached=True))

                # Get number of records
                Albums = unicode(len(AlbumPage.by_tag("tbody")[0].by_tag("tr")))

            print str(page)
            writer.writerow([Name, Genre, Location, Status, YearsActive, Albums])
            
        # Go to next page
        page += 1

    else:
        page = 5

output.close()
