import os
from dateutil import parser
from frontmatter import load, loads
from datetime import datetime
from dataclasses import dataclass

TEMPLATES_DIR = ["templates"] 
COMPONENTS_DIR = ["components"]
OUT_DIR = ["out"]
BLOG_INDIR = ["blog"]
BLOG_OUTDIR = [*OUT_DIR, "blog"]

PAGE_TEMPLATE = [*TEMPLATES_DIR, "page.html"]
BLOGPOST_TEMPLATE = [*TEMPLATES_DIR, "blogpost.html"]

NAVBAR = [*COMPONENTS_DIR, "navbar.html"]
FOOTER = [*COMPONENTS_DIR, "footer.html"]

INDEX_INPUT = ["index.md"]
ABOUT_INPUT = ["about.md"]

STYLE = ["styles.css"]

INDEX_OUTPUT = [*OUT_DIR, "index.html"]
ABOUT_OUTPUT = [*OUT_DIR, "about.html"]
BLOG_OUTPUT = [*BLOG_OUTDIR, "index.html"]

DEFAULT_ARGS = { "nav": "/".join(NAVBAR), "foot": "/".join(FOOTER), "styles": "/".join(STYLE) }

RFC_822_FORMAT = "%a, %d %b %Y %H:%M:%S +0000"

def write(f, c):
    with open(f, "w") as w:
        w.write(c)
def read(f) -> str:
    with open(f, "r") as r:
        return r.read()

## TYPES ##

# Path #
Path = list[str]

# BlogPost #
@dataclass
class BlogPost():
    published_date: datetime
    updated_date: datetime
    title: str
    contents: str
    location: Path 
    def __eq__(self, value: object) -> bool:
        return isinstance(value, BlogPost) and (self.published_date == value.updated_date)
    def __ne__(self, value: object) -> bool:
        return not (self==value)
    def __gt__(self, value: object) -> bool:
        return isinstance(value, BlogPost) and (self.published_date > value.published_date)
    def __lt__(self, value: object) -> bool:
        return isinstance(value, BlogPost) and (self.published_date < value.published_date)
    def __le__(self, value: object) -> bool:
        return not (self > value)
    def __ge__(self, value: object) -> bool:
        return not (self < value)
    @classmethod
    def from_file(cls, file_name: Path):
        parsed = load('/'.join(file_name))
        published_date: datetime = parser.isoparse(str(parsed['published']))
        updated_date: datetime = parser.isoparse(str(parsed['updated']))
        return cls(published_date, updated_date, str(parsed['title']), parsed.content, [*BLOG_OUTDIR, file_name[-1].replace(".md", ".html")])
    def to_rss(self) -> str:
        write(".rsscontent.md", self.contents)
        os.system(f"pandoc .rsscontent.md -o .rsscontent.html")
        content_html = read(".rsscontent.html")
        os.remove(".rsscontent.md")
        os.remove(".rsscontent.html")
        return f"<item><title>{self.title}</title><link>https://benraz.dev/{'/'.join(self.location[1:])}</link><description>{content_html}</description><pubDate>{self.published_date.strftime(RFC_822_FORMAT)}</pubdate></item>"
def build_page(input_page: str | Path, output_page: str | Path, template: str | Path, args: dict[str, str]):
    if isinstance(input_page, list):
        input_page = "/".join(input_page)
    if isinstance(output_page, list):
        output_page = "/".join(output_page)
    if isinstance(template, list):
        template = "/".join(template)
    print(f"[INFO] Transforming Page '{input_page}' into Page '{output_page}' with Template '{template}'")
    command = f"pandoc '{input_page}' -o '{output_page}' --template '{template}' "
    for (arg, val) in args.items():
        command += f"-V {arg}=\"$(cat {val})\" "
    os.system(command)
def build_index_page():
    build_page(INDEX_INPUT, INDEX_OUTPUT, PAGE_TEMPLATE, DEFAULT_ARGS)
def build_about_page():
    build_page(ABOUT_INPUT, ABOUT_OUTPUT, PAGE_TEMPLATE, DEFAULT_ARGS)
def build_blog_posts() -> list[BlogPost]:
    posts = []
    for file in os.listdir("/".join(BLOG_INDIR)):
        post = BlogPost.from_file([*BLOG_INDIR, file])
        posts.append(post)
        build_page([*BLOG_INDIR, file], post.location, BLOGPOST_TEMPLATE, DEFAULT_ARGS)
    return posts
def build_blog_index(posts: list[BlogPost]):
    markdown = "---\ntitle: Blog - Ben Raz\n---\n\n# Blog [(RSS)](/feed.rss)\n"
    for post in reversed(sorted(posts)):
        formatted_date = post.published_date.strftime("[%Y-%m-%d %Z]")
        markdown += \
                f"- <a href='{'/'+'/'.join(post.location[1:])}'>\"{post.title}\"</a> <span class='timestamp'>`{formatted_date}`</span> \n"
    write(".blogpostindex.md", markdown)
    build_page(".blogpostindex.md", BLOG_OUTPUT, PAGE_TEMPLATE, DEFAULT_ARGS)
    os.remove(".blogpostindex.md")
def build_rss_feed(posts: list[BlogPost]):
    rss = f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Ben Raz Blog</title><link>https://benraz.dev/blog</link><description>My beautiful blog, delivered to you with next-generation RSS technology</description><pubDate>{datetime.now().strftime(RFC_822_FORMAT)}</pubDate>{' '.join([post.to_rss() for post in posts])}</channel></rss>'
    write('/'.join([*OUT_DIR, "feed.rss"]), rss)
def publish_changes():
    print("[INFO] Publishing Changes")
    os.system(f"cd {OUT_DIR[0]}; git add .; git commit -sm 'Updated Website'; git push origin main 0>/dev/null")
def main():
    build_index_page()
    build_about_page()
    posts = build_blog_posts()
    build_blog_index(posts)
    publish_changes() if '-p' in ''.join(os.environ) else None

main() if __name__ == "__main__" else None
