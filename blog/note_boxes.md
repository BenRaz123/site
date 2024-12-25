---
title: Note Boxes!
published: 2024-12-24 09:35:00 -05 
updated: 2024-12-24 09:35:00 -05
---

::: note
What I am referring to as _note boxes_ are also referred to more generically as call-out boxes or admonitions boxes. I have not seen it referred to as note boxes before so I have taken it upon myself to contribute to linguistic diversity[^1].
:::

I decided to write a shorter and more lighthearted blog post after my heaver and significantly darker blog post on foreign affairs ([read it here](/blog/trump_ukraine_nato.html)), my topic, as the title suggests, is on note boxes, but not just any note boxes, the ones on my website!

## Demo

The way that my blog works is that posts are written in [markdown](https://en.wikipedia.org/wiki/Markdown) and processed with [pandoc](https://pandoc.org/) into [HTML](https://developer.mozilla.org/en-US/docs/Web/HTML). (For more information on this process read [this](/blog/website_process.html) blog post I wrote.

Anyways, if I write markdown along the lines of this:

```markdown
::: note
Hello World
:::
```

It will evaluate to the following HTML:

```html
<div class="note">
    <p>NOTE:</p>
    <p>Hello World</p>
</div>
```

Which will render like this:

::: note
Hello World
:::

## The Markdown Side of Things

Now, `pandoc` interprets markdown in the format as this:

    ::: <names>
    <content>
    :::

To mean HTML looking like this:

```html
<div class="<names>">
    <content>
</div>
```

The strengths of writing markdown like this is that it is super easy to do and you don't repeat yourself at all (follows DRY). In other words, this type of markdown is very elegant to write. The weaknesses of writing like this is of course that by default and without `css`/`js` this HTML displays exactly the same as everything else.

## The Style Side of Things

If we wanted to add a yellow background color to all note boxes, we would write the following `css`:

```css
div.note {
    background-color: yellow;
}
```

<!-- 
TODO: Make sure GH Link is valid 
-->

::: note
Realistically, that's not all you would do to get a good looking box but I want to keep the post simple. The actual `css` for this site can be viewed at [my GitHub](https://github.com/BenRaz123/site/blob/main/styles.css)
:::

Additionally, each note box has a little tag describing it (e.g. "Note", "Warning", etc). In order to add this tag without `js` we will write this code:

```css
div.note::before {
    content: "Note";
    margin-left: -1em;
}
```

Since the first `<p>` element is now redundant, we can remove it like this:

```css
div.note > p:first-child { display: none }
```

This is nice because boxes will be legible without `css` but will look nice with `css` as well. And all of this without a single line of JavaScript!. 

### Generalizing

Now all of this is fine and dandy until we want to define additional note boxes, like `Warning`, `Info`, and etc[^2]. As you can see with the following `css`, the naive approach can get annoying quickly:

```css
/*
 * Notes
 */

div.note {
    background-color: yellow;
    /* ... */
}

div.note::before {
    content: "Note";
    margin-left: -1em;
    /* ... */
}

div.note > p:first-child { display: none; }

/*
 * Warning
 */

div.warning {
    background-color: red;
    /* ... */
}

div.warning::before {
    content: "Warning";
    margin-left: -1em;
    /* ... */
}

div.warning > p:first-child { display: none; }

/*
 * Info
 */

div.info {
    background-color: gray;
    /* ... */
}

div.info::before {
    content: "Info";
    margin-left: -1em;
    /* ... */
}

div.info > p:first-child { display: none; }
```

Even if we use CSS nesting, this code looks no prettier:

```css
div.note {
    background-color: yellow;
    /* ... */
    & ::before {
        content: "Note";
        margin-left: -1em;
        /* ... */
    }

    & > p:first-child {
        display: none;
    }
}

div.warning {
    background-color: red;
    /* ... */
    & ::before {
        content: "Warning";
        margin-left: -1em;
        /* ... */
    }

    & > p:first-child {
        display: none;
    }
}

div.info{
    background-color: gray;
    /* ... */
    & ::before {
        content: "Info";
        margin-left: -1em;
        /* ... */
    }

    & > p:first-child {
        display: none;
    }
}
```

Additionally, we should be able to accommodate much more boxes, like `Hint`, `Disclaimer`[^3], and so on. And we should have a default box as any box that isn't covered in the CSS simply isn't styled. The solution to this is to stop repeating ourselves and to generalize. We can do this by using the `[class]` selector and the `attr()` function to abstract over class:

```css
div[class] {
    background-color: gray;
    /* ... */
    & ::before {
        content: attr(class);
        text-transform: capitalize;
        margin-left: -1em;
        /* ... */
    }

    & > p:first-child {
        display: none;
    }
}
```

This is the generic solution, which covers all possible classes. From here we can define specific cases (this is because the `div.<class>` selector is more specific than the `div[class]` selector):

```css
div.note {
    background-color: yellow;
}

div.warning {
    background-color: red;
}
```

And so thus, our --- one could say Object Oriented --- CSS solution manages to solve the problem of code duplication by creating a default and implementation and "classes" that override this implementation.

## The `Pandoc` Side of Things

Now, the avid readers will wonder where the `NOTE:` is added in the build process. This is something done note with Python (build script), JavaScript, or CSS. This is actually done via a `pandoc` filter written using `lua` (filters are invoked using `pandoc --lua-filter <file>`). The filter takes a

```markdown
::: <text>
<content>
:::
```

and transforms it into

```markdown
::: <text>
<TEXT>:
<content>
:::
```

Here is the code for the filter:

```lua
function Div(el)
    if #el.classes > 0 then
        local some_word = el.classes[1]
        local capitalized_word = string.upper(some_word)
        local capitalized_intro = pandoc.Para({pandoc.Str(capitalized_word .. ":")})
        table.insert(el.content, 1, capitalized_intro)
    end
    return el
end
```

This filter checks for a div element with a non-zero amount of classes, and appends the class name to the content in uppercase.

[^1]: Or, for the cynical, linguistic fragmentation
[^2]: I even defined a `Carrots/Sticks` box! (Used [on this blog post about geopolitics](/blog/trump_ukraine_nato.html#the-new-strategy)
[^3]: ... and `Carrots/Sticks` of course ;)
