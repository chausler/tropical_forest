import json
import re
from datetime import date
published_ex = re.compile(r'<published>(\d{4})-(\d{2})-(\d{2}).+?</published>')
title_ex = re.compile(r'<title>(.+?)</title>', flags=re.DOTALL)
summary_ex = re.compile(r'<summary>(.+?)</summary>', flags=re.DOTALL)
author_ex = re.compile(r'<name>(.+?)</name>')
link_ex = re.compile(r'<id>(.+?)</id>')


example = """ <id>http://arxiv.org/abs/physics/0303043v1</id>
    <updated>2003-03-11T08:53:41Z</updated>
    <published>2003-03-11T08:53:41Z</published>
    <title>Geometric phase due to helicity inversion of photons inside an optical
  fiber composed periodically of left- and right- handed media</title>
    <summary>  In this Letter, it is claimed that, in addition to the Chiao-Wu geometric
phase and optical Aharonov-Carmi geometric phase, there exists a new
interesting geometric phase caused by the helicity inversion of photons in the
optical fiber composed periodically of left- and right- handed (LRH) media. By
making use of the Lewis-Riesenfeld invariant theory and the invariant-related
unitary transformation formulation, we calculate this geometric phase. It is
emphasized that this geometric phase should not been neglected when considering
the anomalous refraction on the interfaces between left- and right- handed
media.
</summary>
    <author>
      <name>Jian Qi Shen</name>
    </author>
    <arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">5 pages, Latex</arxiv:comment>
    <link href="http://arxiv.org/abs/physics/0303043v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/physics/0303043v1" rel="related" type="application/pdf"/>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="physics.optics" scheme="http://arxiv.org/schemas/atom"/>
    <category term="physics.optics" scheme="http://arxiv.org/schemas/atom"/>
    <category term="physics.gen-ph" scheme="http://arxiv.org/schemas/atom"/>"""


class Entry:
    def __init__(self, text):
        self.text = text
        self.published = None
        self.title = None
        self.summary = None
        self.author = None
        self.link = None
        self._get_ready()

    def _get_ready(self):
        self._get_published()
        self._get_title()
        self._get_summary()
        self._get_author()
        self._get_link()

    def _get_published(self):
        match = re.search(published_ex, self.text)
        if match:
            year = match.group(1)
            month = match.group(2)
            day = match.group(3)
            self.published = date(int(year), int(month), int(day))

    def _get_title(self):
        match = re.search(title_ex, self.text)
        if match:
            self.title = match.group(1).replace('\n', '')

    def _get_summary(self):
        match = re.search(summary_ex, self.text)
        if match:
            self.summary = match.group(1).replace('\n', ' ').strip()

    def _get_author(self):
        match = re.search(author_ex, self.text)
        if match:
            self.author = match.group(1)

    def _get_link(self):
        match = re.search(link_ex, self.text)
        if match:
            self.link = match.group(1)

    def to_dict(self):
        y, m, d = self.published.year, self.published.month, self.published.day
        return {'published': { 'year': y, 'month': m, 'day': d },
                'title': self.title,
                'summary': self.summary,
                'author': self.author,
                'link': self.link}

if __name__ == '__main__':
    lst = json.load(open('arxiv_2000_2016.json'))
    entries = [Entry(x).to_dict() for x in lst][:500]
    json.dump(entries, open('arxiv_sample.json', 'w'))
