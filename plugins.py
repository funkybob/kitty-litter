import typing
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin

from lxml import etree, html
from lxml.builder import ElementMaker

from stencil import SafeStr

from gilbert import Site
from gilbert.content import Renderable, Content
from gilbert.plugins.selection import Selection
from gilbert.plugins.markdown import MarkdownPage
from gilbert.utils import oneshot


class BlogPost(MarkdownPage):
    template = "blog/post_detail.html"


class RecipePost(MarkdownPage):
    template = 'recipes/detail.html'


class TagIndex(Selection):
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


ATOM_NAMESPACE = 'http://www.w3.org/2005/Atom'

RSS = ElementMaker(nsmap={'atom': ATOM_NAMESPACE})
ATOM = ElementMaker(namespace=ATOM_NAMESPACE)


class RssFeed(Renderable, Content):
    selection: str
    output_extension = 'xml'

    def render(self):
        cfg = self.site.config

        url = cfg['global']['url']

        selection = self.site.content[self.selection]

        items = [
            RSS.item(
                RSS.title(page.title),
                RSS.link(urljoin(url, str(page.output_filename))),
                RSS.guid(urljoin(url, str(page.output_filename))),
                RSS.description(''),
            )
            for page in selection.pages
        ]

        doc = RSS.rss(
            RSS.channel(
                RSS.title(cfg['global']['sitename']),
                RSS.link(url),
                ATOM.link(
                    rel="self",
                    href=urljoin(url, str(self.output_filename)),
                ),
                RSS.description("FunkyBob's Blog"),
                *items,
            ),
            version="2.0",
        )

        target = self.site.dest_dir / self.output_filename
        target.write_bytes(etree.tostring(doc, pretty_print=True))


def excerpt(content, length):
    fragments = html.fromstring(content)
    return SafeStr(''.join(
        html.tostring(x, encoding='unicode')
        for x in fragments[:length]
    ))


@Site.register_context_provider
def global_context(ctx):

    ctx['excerpt'] = excerpt
    ctx['safe'] = SafeStr

    return ctx
