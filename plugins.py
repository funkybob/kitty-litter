import typing
from collections import Counter
from pathlib import Path

import yaml

from stencil import SafeStr

from gilbert import Site
from gilbert.plugins.collection import Collection
from gilbert.plugins.markdown import MarkdownPage
from gilbert.utils import oneshot


class BlogPost(MarkdownPage):
    template = "blog/post_detail.html"


class TagIndex(Collection):
    exclude_tags: typing.Collection[str] = set()
    template = 'tag_index.html'

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
                target.write_text(template.render(ctx))


import html5lib

def truncate(html, length):
    stream = html5lib.parse(html[:length])
    return SafeStr(html5lib.serializer.serialize(stream))


@Site.register_context_provider
def global_context(ctx):

    ctx['shorten'] = truncate
    ctx['safe'] = SafeStr

    return ctx
