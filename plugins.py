import typing
from collections import Counter
from operator import attrgetter

from gilbert.content import Content, Templated
from gilbert.query import Query
from gilbert.utils import oneshot


class Menu(Templated, Content):
    template = 'menu.html'
    sort_by = 'name'

    filter_by : dict = {}

    @oneshot
    def pages(self):
        sort_by = self.sort_by
        reverse = sort_by.startswith('-')
        if reverse:
            sort_by = sort_by[1:]
        key = attrgetter(sort_by)
        return sorted(
            self.site.pages.matching(self.filter_by),
            key=key,
            reverse=reverse,
        )


class TagCloud(Content):
    exclude_tags : typing.Collection[str] = set()

    filter_by : dict = {}

    @oneshot
    def tag_counts(self):
        tags = Counter()
        for obj in self.site.pages.matching(self.filter_by):
            tags.update(tag for tag in obj.tags if tag not in self.exclude_tags)
        return tags
