import typing
from collections import Counter
from pathlib import Path

import yaml

from gilbert import Site
from gilbert.plugins.collection import Collection
from gilbert.utils import oneshot


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

        for tag in self.tag_counts:
            ctx = self.site.get_context(self)
            target = target_path / f'{tag}.html'
            with ctx.push({
                'tag': tag,
                'pages': [page for page in self.pages if tag in page.tags]
            }):
                target.write_text(template.render(ctx))


import html5lib

def truncate(html, length):
    stream = html5lib.parse(html[:length])
    return html5lib.serializer.serialize(stream)


@Site.register_context_provider
def global_context(ctx):

    with open('global.yml') as fin:
        ctx.update(yaml.load(fin, Loader=yaml.Loader))

    ctx['shorten'] = truncate

    return ctx
