import typing
from collections import Counter
from operator import attrgetter
from pathlib import Path

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


class TagIndex(Content):
    exclude_tags : typing.Collection[str] = set()
    template = 'tag_index.html'

    filter_by : dict = {}

    @oneshot
    def pages(self):
        return self.site.pages.matching(self.filter_by)

    @oneshot
    def tag_counts(self):
        tags = Counter()
        for obj in self.pages:
            tags.update(tag for tag in obj.tags if tag not in self.exclude_tags)
        return tags

    def render(self):
        target_path = self.site.dest_dir / Path(self.name).with_suffix('')
        target_path.mkdir(parents=True, exist_ok=True)

        template = self.site.templates[self.template]
        ctx = self.site.get_context(self)

        for tag in self.tag_counts:
            target = target_path / f'{tag}.html'
            with ctx.push({
                'tag': tag,
                'pages': [page for page in self.pages if tag in page.tags]
            }):
                target.write_text( template.render(ctx) )
