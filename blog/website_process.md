---
title: The Process of Building This Website
published: 2024-10-30 17:00:00 -04
updated: 2024-11-1 11:25:00 -04
description: A description of the process behind building my website
---

::: info
The source for this website can be found on my Github at [this link](https://github.com/benraz123/site). This site is hosted at [this link](https://github.com/benraz123/benraz123.github.io).
:::

Welcome again to my brand-new website! I hope it doesn't look too terrible. I wanted to, in an act of supreme originality, dedicate my first blog post to documenting the process used to conjure up this website, READMEs be damned. 

## The Original Idea

My primary goal with this project was to build a low-effort text-oriented website. In order to make the hosting simple (I am using Github Pages here), a static output directory was needed. Additionally, creating an RSS feed was another goal, as while clearly the vast majority of people disagree with me, RSS feeds provide a superior user-experience. Why go to one website after another when you can see them all in one uniform, customisable reader that can be used offline and/or the terminal (yes, I know command-line browsers exist, but they are unusable for pretty much every single modern website). Now, I could have all of this by just writing HTML by hand, but where's the fun in that? I'm a developer after all, which means I am dangerously addicted to Markdown (and sometimes orgmode). So my website's content should be written in markdown and converted to html.

## How to do it

We are in luck, as it turns out. Not only was Markdown written _for the purpose of_ being converted to HTML, many converters from Markdown to HTML exist. The best of them in my experience is [`pandoc`](https://pandoc.org). `pandoc` allows not just for converting markdown to html but also using templates. This is where the fun begins. 

### A Basic `Pandoc` Template

A basic `pandoc` template would look like this:

```html
<title>$title$</title>
<body>
    Author: $author$
    <hr>
    $content$
</body>
```

If we write the following markdown:

```markdown
---
title: Hello World
author: Albert Einstein
---

This is a very simple thing.
```

We could build it with the following command:

```
pandoc in.md -o out.html --template template.html
```

This would produce the following document:

```html
<title>Hello World</title>
<body>
    <p>Author: Albert Einstein</p>
    <hr>
    <p>This is a very simple thing</p>
</body>
```

This allows for us to use a sort of component system. For example, instead of writing the same navigation bar for two different templates, I can just parameterize the navigation bar. In my template file, I write this:

```html
...
$navbar$
...
```

And I compile with the `-V navbar="$(cat navbar.html)"` flag. Just like that, we have a working component system (sort of). Putting all of this together, we have a working static site generator. I recommend the following directory structure as well:

```
/ (project root)
- blog/
- templates/
- components/
- out/
  - blog/
```

## The Build Stage

Now in order to put this all together, I whipped up a quick python script to build the site automatically, because running `pandoc` by hand get's annoying, difficult, and error-prone if one has dozens of posts. I debated if I should have used `bash`, `make`, or even `fish`, but `python` ultimately won out as it is the simplest for me and allows for the most "programming", useful because I do end up (sort of) serializing the blog posts.

The heart of the script is the function `build_page()`. This function basically just wraps around a `pandoc` command to build a page with a template and add components. Here it is:

```python
def build_page(input_page: str, output_page: str, template: str, args: dict[str, str]):
    print(f"[INFO] Transforming Page '{input_page}' into Page '{output_page}' with Template '{template}'")
    command = f"pandoc '{input_page}' -o '{output_page}' --template '{template}' "
    for (arg, val) in args.items():
        command += f"-V {arg}=\"$(cat {val})\" "
    os.system(command)
```

With this handy function, generating the about and index pages becomes very easy. All we have to do is run the `build_page()` function like this:

```python
# Generate Index Page
build_page("index.md", "out/index.html", "templates/page.html", DEFAULT_ARGS)
# Generate About Page
build_page("about.md", "out/about.html", "templates/page.html", DEFAULT_ARGS)
```

The next thing to do is to build the blog posts and the blog index. For this I decided for some reason to abstract over a blog post with a class. However, in my defense, it was a `dataclass`.

```python
@dataclass
class BlogPost():
    published_date: datetime
    updated_date: datetime
    title: str
    contents: str
    location: list[str] 
```

Why so many properties? The main reason was I wanted to be able to sort, list, and make into an RSS feed the blog posts. I additionally wrote the boilerplate necessary for sorting a `list[BlogPost]` (`__eq__()`, `__ne__()`, `__gt__()`, `__lt__()`, `__ge__()`, and `__le__()`).

I wrote a function next for getting all blog posts and building all of them. After a little `CSS`, it's all done.

## Putting it all Together 

::: warning
While effort was made to make the script generic, it still contains a lot of hardcoded values. Additionally, it is not well-written or tested so do not expect for it to work. If you don't want to get down and dirty in the details, don't use it. There are plenty of SSGs around and I don't want to rob you of the fun of writing your own.
:::

To summarize, I basically created a crappy SSG with `python` and `pandoc`. If anyone for any reason wants to see it, the site is contained in two repositories, [this one](https://github.com/benraz123/site) for the source and [this one](https://github.com/benraz123/benraz123.github.io) for the build. 
