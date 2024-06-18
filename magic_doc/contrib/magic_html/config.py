# -*- coding:utf-8 -*-

Unique_ID = "all_ids_pjtest_20300101_921b9a"

PAYWALL_DISCARD_XPATH = [
    """.//*[(self::div or self::p)][
    contains(@id, "paywall") or contains(@id, "premium") or
    contains(@class, "paid-content") or contains(@class, "paidcontent") or
    contains(@class, "obfuscated") or contains(@class, "blurred") or
    contains(@class, "restricted") or contains(@class, "overlay")
    ]""",
]

OVERALL_DISCARD_XPATH = [
    # navigation + footers, news outlets related posts, sharing, jp-post-flair jp-relatedposts
    """.//*[(self::div or self::item or self::ul
             or self::p or self::section or self::span)][
    contains(translate(@id, "F","f"), "footer") or contains(translate(@class, "F","f"), "footer")
    or contains(@id, "related") or contains(translate(@class, "R", "r"), "related") or
    contains(@id, "viral") or contains(@class, "viral") or
    starts-with(@id, "shar") or starts-with(@class, "shar") or
    contains(@class, "share-") or
    contains(translate(@id, "S", "s"), "share") or
    contains(@id, "social") or contains(@class, "social") or contains(@class, "sociable") or
    contains(@id, "syndication") or contains(@class, "syndication") or
    starts-with(@id, "jp-") or starts-with(@id, "dpsp-content") or
    contains(@class, "embedded") or contains(@class, "embed")
    or contains(@id, "newsletter") or contains(@class, "newsletter")
    or contains(@class, "subnav") or
    contains(@id, "cookie") or contains(@class, "cookie") or contains(@id, "tags")
    or contains(@class, "tags")  or contains(@id, "sidebar") or
    contains(@class, "sidebar") or contains(@id, "banner") or contains(@class, "banner")
    or contains(@class, "meta") or
    contains(@id, "menu") or contains(@class, "menu") or
    contains(translate(@id, "N", "n"), "nav") or contains(translate(@role, "N", "n"), "nav")
    or starts-with(@class, "nav") or contains(translate(@class, "N", "n"), "navigation") or
    contains(@class, "navbar") or contains(@class, "navbox") or starts-with(@class, "post-nav")
    or contains(@id, "breadcrumb") or contains(@class, "breadcrumb") or
    contains(@id, "bread-crumb") or contains(@class, "bread-crumb") or
    contains(@id, "author") or contains(@class, "author") or
    contains(@id, "button") or contains(@class, "button")
    or contains(translate(@class, "B", "b"), "byline")
    or contains(@class, "rating") or starts-with(@class, "widget") or
    contains(@class, "attachment") or contains(@class, "timestamp") or
    contains(@class, "user-info") or contains(@class, "user-profile") or
    contains(@class, "-ad-") or contains(@class, "-icon")
    or contains(@class, "article-infos") or
    contains(translate(@class, "I", "i"), "infoline")
    or contains(@data-component, "MostPopularStories")
    or contains(@class, "outbrain") or contains(@class, "taboola")
    or contains(@class, "criteo") or contains(@class, "options")
    or contains(@class, "consent") or contains(@class, "modal-content")
    or contains(@class, "paid-content") or contains(@class, "paidcontent")
    or contains(@id, "premium-") or contains(@id, "paywall")
    or contains(@class, "obfuscated") or contains(@class, "blurred")
    or contains(@class, " ad ")
    or contains(@class, "next-post")
    or contains(@class, "yin") or contains(@class, "zlylin") or
    contains(@class, "xg1") or contains(@id, "bmdh")
    or @data-lp-replacement-content]""",
    # hidden parts
    """.//*[starts-with(@class, "hide-") or contains(@class, "hide-print") or contains(@id, "hidden")
    or contains(@style, "hidden") or contains(@hidden, "hidden") or contains(@class, "noprint")
    or contains(@style, "display:none") or contains(@class, " hidden") or @aria-hidden="true"
    or contains(@class, "notloaded")]""",
    # comment debris
    # or contains(@class, "message-container") or contains(@id, "message_container")
    """.//*[@class="comments-title" or contains(@class, "comments-title") or
    contains(@class, "nocomments") or starts-with(@id, "reply-") or starts-with(@class, "reply-") or
    contains(@class, "-reply-") or contains(@class, "message") or contains(@id, "message_container")
    or contains(@id, "akismet") or contains(@class, "akismet")] """,
]

TEASER_DISCARD_XPATH = [
    """.//*[(self::div or self::item or self::ul
             or self::p or self::section or self::span)][
        contains(translate(@id, "T", "t"), "teaser") or contains(translate(@class, "T", "t"), "teaser")
    ]""",
]

PRECISION_DISCARD_XPATH = [
    ".//header",
    """.//*[(self::div or self::item or self::ul
             or self::p or self::section or self::span)][
        contains(@id, "bottom") or contains(@class, "bottom") or
        contains(@id, "link") or contains(@class, "link")
        or contains(@style, "border")
    ]""",
]

DISCARD_IMAGE_ELEMENTS = [
    """.//*[(self::div or self::item or self::ul
             or self::p or self::section or self::span)][
             contains(@id, "caption") or contains(@class, "caption")
            ]
    """
]

REMOVE_COMMENTS_XPATH = [
    """.//*[(self::div or self::ul or self::section)][
    starts-with(translate(@id, "C","c"), 'comment') or
    starts-with(translate(@class, "C","c"), 'comment') or starts-with(translate(@name, "C","c"), 'comment') or
    contains(@class, 'article-comments') or contains(@class, 'post-comments')
    or starts-with(@id, 'comol') or starts-with(@id, 'disqus_thread')
    or starts-with(@id, 'dsq-comments')
    ]"""
]

CONTENT_EXTRACTOR_NOISE_XPATHS = [
    # '//div[contains(@class, "comment") or contains(@name, "comment") or contains(@id, "comment")]',
    '//div[starts-with(@class, "advert") or starts-with(@name, "advert") or starts-with(@id, "advert")]',
    '//div[contains(@style, "display: none")]',
    '//div[contains(@style, "display:none")]',
]

# 保留图片，音频，视频
MANUALLY_CLEANED = [
    "aside",
    "embed",
    "footer",
    "head",
    "iframe",
    "menu",
    "object",
    "script",
    "applet",
    "canvas",
    "map",
    "svg",
    "area",
    "blink",
    "button",
    "datalist",
    "dialog",
    "frame",
    "frameset",
    "fieldset",
    "link",
    "input",
    "ins",
    "label",
    "legend",
    "marquee",
    "menuitem",
    "nav",
    "noscript",
    "optgroup",
    "option",
    "output",
    "param",
    "progress",
    "rp",
    "rt",
    "rtc",
    "select",
    "style",
    "track",
    "textarea",
    "time",
    "use",
]

MANUALLY_STRIPPED = [
    "abbr",
    "acronym",
    "address",
    "bdi",
    "bdo",
    "big",
    "cite",
    "data",
    "dfn",
    "font",
    "hgroup",
    "ins",
    "mark",
    "meta",
    "ruby",
    "small",
    "tbody",
    "template",
    "tfoot",
    "thead",
]

CUT_EMPTY_ELEMS = {
    "article",
    "b",
    "blockquote",
    "dd",
    "div",
    "dt",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "i",
    "li",
    "main",
    "p",
    "pre",
    "q",
    "section",
    "span",
    "strong",
}

USELESS_ATTR = [
    "share",
    "contribution",
    "copyright",
    "copy-right",
    "disclaimer",
    "recommend",
    "related",
    "footer",
    "social",
    "submeta",
    "report-infor",
]

BODY_XPATH = [
    """.//*[(self::article or self::div or self::main or self::section)][
    @class="post" or @class="entry" or
    contains(@class, "post-text") or contains(@class, "post_text") or
    contains(@class, "post-body") or contains(@class, "post-entry") or contains(@class, "postentry") or
    contains(@class, "post-content") or contains(@class, "post_content") or
    contains(@class, "postcontent") or contains(@class, "postContent") or
    contains(@class, "article-text") or contains(@class, "articletext") or contains(@class, "articleText")
    or contains(@id, "entry-content") or
    contains(@class, "entry-content") or contains(@id, "article-content") or
    contains(@class, "article-content") or contains(@id, "article__content") or
    contains(@class, "article__content") or contains(@id, "article-body") or
    contains(@class, "article-body") or contains(@id, "article__body") or
    contains(@class, "article__body") or @itemprop="articleBody" or
    contains(translate(@id, "B", "b"), "articlebody") or contains(translate(@class, "B", "b"), "articlebody")
    or @id="articleContent" or contains(@class, "ArticleContent") or
    contains(@class, "page-content") or contains(@class, "text-content") or
    contains(@id, "body-text") or contains(@class, "body-text") or contains(@class, "body-content") or contains(translate(@class, "B", "b"), "textbody") or 
    contains(@class, "article__container") or contains(@id, "art-content") or contains(@class, "art-content")][1]""",
    "(.//article)[1]",
    """(.//*[(self::article or self::div or self::main or self::section)][
    contains(@class, 'post-bodycopy') or
    contains(@class, 'storycontent') or contains(@class, 'story-content') or
    @class='postarea' or @class='art-postcontent' or
    contains(@class, 'theme-content') or contains(@class, 'blog-content') or
    contains(@class, 'section-content') or contains(@class, 'single-content') or
    contains(@class, 'single-post') or
    contains(@class, 'main-column') or contains(@class, 'wpb_text_column') or
    starts-with(@id, 'primary') or starts-with(@class, 'article ') or @class="text" or
    @id="article" or @class="cell" or @id="story" or @class="story" or
    contains(@class, "story-body") or contains(@class, "field-body") or
    contains(translate(@class, "FULTEX","fultex"), "fulltext")
    or @role='article'])[1]""",
    """(.//*[(self::article or self::div or self::main or self::section)][
    contains(@id, "content-main") or contains(@class, "content-main") or contains(@class, "content_main") or
    contains(@id, "content-body") or contains(@class, "content-body") or contains(@id, "contentBody")
    or contains(@class, "content__body") or contains(translate(@id, "CM","cm"), "main-content") or contains(translate(@class, "CM","cm"), "main-content")
    or contains(translate(@class, "CP","cp"), "page-content") or
    @id="content" or @class="content"])[1]""",
    '(.//*[(self::article or self::div or self::section)][starts-with(@class, "main") or starts-with(@id, "main") or starts-with(@role, "main")])[1]|(.//main)[1]',
]

Forum_XPATH = [
    """.//*[(self::article or self::div or self::main or self::section or self::li or self::tr)][
    contains(@id, 'question') or contains(@class, 'question')]""",
    """.//*[(self::article or self::div or self::main or self::section or self::li or self::tr)][
    contains(@id, 'answer') or contains(@class, 'answer')]""",
    """.//*[(self::article or self::div or self::main or self::section or self::li or self::tr)][
    contains(@id, 'comment') or contains(@class, 'comment') or contains(@class, 'Comment')]""",
    """.//*[(self::article or self::div or self::main or self::section or self::li or self::tr)][contains(@class, "message-container") or contains(@id, "message_container") or contains(@class, "Messages_container")]""",
    """.//*[(self::article or self::div or self::main or self::section or self::p or self::span or self::li or self::tr)][
    contains(@id, 'comment-content') or contains(@class, 'comment-content') or contains(@class, 'comment-body') or contains(@class, 'comment-body') or contains(@class, "post-reply") or contains(@class, "reply_content") or contains(@class, "reply-content") or contains(@class, "reply_post") or contains(@class, "post-reply") or contains(@id, "reply") or contains(@class, "post-text") or contains(@class, "post_text") or
    contains(@class, "post-body") or contains(@class, "postbody") or contains(@class, "post-entry") or contains(@class, "postentry") or contains(@component, 'post') or 
    contains(@class, "post-content") or contains(@class, "post_content") or contains(@class, "p_content") or contains(@class, "Post_content") or contains(@class, "message-post") or contains(@class, "js-post")]""",
    # id 包含post-加数字组成的形式
    """.//*[(self::article or self::div or self::main or self::section or self::p or self::span or self::li or self::tr)][contains(@id, 'post-') or contains(@id, 'post_')]"""
]

METAS = [
    '//meta[starts-with(@property, "og:title")]/@content',
    '//meta[starts-with(@name, "og:title")]/@content',
    '//meta[starts-with(@property, "title")]/@content',
    '//meta[starts-with(@name, "title")]/@content',
    '//meta[starts-with(@property, "page:title")]/@content',
    '//meta[starts-with(@name, "page:title")]/@content',
]
