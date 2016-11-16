% Degrees of Rudi Völler - Neo4j Edition

Graph databases are the [new][gdbarticle] [hot][ibmgraph]
[thing][neo4jgraph]. Actually [not so new][wikigraph]. IBM, among
others, has been toying with them since the 1960s. In recent years
they have been popularized through
[social media analysis][neo4jsocial] and people have realized that
they can be used for a lot of other interesting things like, but not
limited to:

- Fraud detection.
- Recommendation engines.
- Graph based search.
- Master data management.

For us data scientists graph databases are an important tool that all
of us should have at least some familiarity with. They are no silver
bullet, but used right they can lead to simpler solutions in
situations where traditional databases just won't cut it.

Enough talk, let me walk you through an example in [Neo4j], centered
around historical and current members of the
[German national soccer team][desoccer]. I'll leave it as an exercise
to the interested reader to make the connection to possible
applications to fraud detection or recommendation engines.

Neo4j provides a free community edition which works great and is
[well documented][neo4jdoc]. It is very quick to set up, for testing
and evaluation purposes all you have to do is download the latest
release and run an executable. You can send queries to and inspect
results from Neo4j in your web browser, easy as pie.

## Getting The Data - Web Scraping

To get some data we have, like so often, to do some [scraping]. I've
mentioned [scrapy] and [beautifulsoup][bs4] several times before. They
are great tools by themselves and virtually unbeatable together. You
can of course parse the DOM tree in pure scrapy (using CSS selectors
or XPATH), which is fine for some simple applications, but I'd
strongly recommend using beautifulsoup for entity extraction in any
serious application. In practice, your parsing function will then
start with something like this:

~~~{.python}
def parse_tournament(self, response):
    soup = BeautifulSoup(response.text, "lxml")
    header = soup.find("span",
        id=re.compile(".*Germany.*")).parent
~~~

All you have to do is `yield` the extracted entities as dictionary and
write the result into a CSV file. You can then load the CSV into Neo4j
as described in their documentation and start having some fun.

## Degrees of Rudi Völler

[Rudi Völler][rv], one of the most prominent past national players,
will serve us as a worthy example. So, where did he play? Easy.

~~~
MATCH (:Player {name: 'Rudi Völler'})-[r:PLAYED]->(c:Club)
RETURN *
~~~

The cypher code above (Neo4j's internal language is call cypher, but
is in contrast to the name's undertone quite easy to use) will give a
result like shown below.

![](https://dataadventuresdotcom.files.wordpress.com/2016/10/voellersimple.png)

Now this is nothing you couldn't easily do in SQL. Yes, in Neo4j's web
interface, you can play around with the blobs and arrows, but that's
more of a gimmick. So let's get more creative. Which are the national
players that managed teams that Mr. Völler played in or managed?

~~~
MATCH (:Player {name: 'Rudi Völler'})-[r]->(c:Club)<-[s:MANAGED]-(p)
RETURN *
~~~

![](https://dataadventuresdotcom.files.wordpress.com/2016/10/voellerfull.png)

Voila. Since the human brain is so good at recognizing patterns
(sometimes even if they're [not really there][pareidolia]), some fraud
analysts use tools like this to visualize suspected fraud rings. But
what if you want to become more quantitative, asking questions like:
Who played in the most clubs that Mr. Völler was either playing for or
managing?

~~~
MATCH (:Player {name: 'Rudi Völler'})-[]->(c:Club)<-[r:PLAYED]-(p)
RETURN p.name, COUNT(r)
ORDER BY -COUNT(r)
LIMIT 5
~~~

+---------------+--------+
|p.name         |COUNT(r)|
+===============+========+
|Thomas Häßler  |3       |
+---------------+--------+
|Oliver Neuville|2       |
+---------------+--------+
|Michael Ballack|2       |
+---------------+--------+
|André Schürrle |2       |
+---------------+--------+
|Stefan Kießling|2       |
+---------------+--------+


Pretty nice, with a syntax easy enough that I tend to require far less
googling that with some SQL dialects when I work with cypher. Now go
on your own data adventure and play around with Neo4j!

[gdbarticle]: https://www.infoq.com/minibooks/emag-graph-databases
[ibmgraph]: https://www.ibm.com/blogs/bluemix/2016/07/graph-databases-natural-way-to-represent-data/
[neo4jgraph]: https://neo4j.com/blog/native-vs-non-native-graph-technology/
[wikigraph]: https://en.wikipedia.org/wiki/Graph_database#History
[neo4jsocial]: https://neo4j.com/use-cases/social-network/
[Neo4j]: https://neo4j.com/
[neo4jdoc]: https://neo4j.com/docs/developer-manual/current/
[desoccer]: https://en.wikipedia.org/wiki/Germany_national_football_team
[scrapy]: http://scrapy.org/
[scraping]: https://en.wikipedia.org/wiki/Web_scraping
[bs4]: https://www.crummy.com/software/BeautifulSoup/
[rv]: https://en.wikipedia.org/wiki/Rudi_V%C3%B6ller
[pareidolia]: https://en.wikipedia.org/wiki/Pareidolia
