# -*- coding: utf8 -*-

import unittest
from phtml import *


class TestPhtml(unittest.TestCase):

    assertEqualWS = unittest.TestCase.assertEqual

    def assertEqual(self, first, second, msg=None):
        """Overriden for ignoring whitespace."""
        def remove_whitespace(s):
            if isinstance(s, basestring):
                return s.replace(' ', '').replace('\n', '')
            else:
                return s
        first = remove_whitespace(first)
        second = remove_whitespace(second)
        return super(TestPhtml, self).assertEqual(first, second, msg)

    def test_tag(self):
        self.assertEqual(str(hr), '<hr/>')
        self.assertEqual(str(html), '<html></html>')
        self.assertEqual(str(html()), '<html></html>')
        self.assertEqual(str(html('')), '<html></html>')
        self.assertEqual(str(html('content')), '<html>content</html>')
        self.assertEqual(str(html(6)), '<html>6</html>')
        self.assertEqual(str(html(lang='tr')), '<html lang="tr"></html>')

        self.assertEqual(str(html()()), '<html></html>')
        self.assertEqual(str(html()('')), '<html></html>')
        self.assertEqual(str(html()('content')), '<html>content</html>')

        self.assertEqual(str(html(lang='tr')()), '<html lang="tr"></html>')
        self.assertEqual(str(html(lang='tr')('')), '<html lang="tr"></html>')
        self.assertEqual(str(html(lang='tr')('content')), '<html lang="tr">content</html>')

    def test_block_fill_str(self):
        h = html(
            head(title('phtml is awesome')),
            body(
                p('a paragraph'),
                Block('main')
            )
        )
        h['main'] = 'yess'
        self.assertEqual(str(h), '<html><head><title>phtml is awesome'\
                                 '</title></head><body><p>a paragraph</p>'\
                                 'yess</body></html>')

    def test_block_fill_tag(self):
        h = html(
            head(title('phtml is awesome')),
            body(
                p('a paragraph'),
                Block('main')
            )
        )
        h['main'] = hr
        self.assertEqual(str(h), '<html><head><title>phtml is awesome'\
                                 '</title></head><body><p>a paragraph</p>'\
                                 '<hr/></body></html>')

    def test_block_fill_lazy(self):
        class V(object):
            def __str__(self):
                return 'asdf'
        v = V()
        h = html(Block('b'))
        h['b'] = v
        self.assertEqual(str(h), '<html>asdf</html>')

    def test_block_placeholder(self):
        h = html(Block('b')('xxx'))
        self.assertEqual(str(h), '<html>xxx</html>')
        h['b'] = 'yyy'
        self.assertEqual(str(h), '<html>yyy</html>')
        h['b'] = 'zzz'
        self.assertEqual(str(h), '<html>zzz</html>')

    def test_find_blocks(self):
        a1 = Block('a')
        a2 = Block('a')
        b = Block('b')
        h = html(
                head(
                    title(Block('title'))
                ),
                body(a1, a2, b)
            )
        _a = h._find_blocks('a')
        self.assertEqual(len(_a), 2)
        self.assertIs(_a[0], a1)
        self.assertIs(_a[1], a2)
        _b = h._find_blocks('b')
        self.assertEqual(_b[0], b)

    def test_reserved_keywords(self):
        t = div(class_='container')
        self.assertEqual(str(t), '<div class="container"></div>')

    def test_copy(self):
        t = div(Block('a'))
        t2 = t.copy()
        t2['a'] = '1'
        self.assertEqual(str(t), '<div></div>')
        self.assertEqual(str(t2), '<div>1</div>')

    def test_escape_tag(self):
        dangerous = '<script>'
        tag = div(dangerous)
        rendered = str(tag)
        self.assertEqual(rendered, '<div>&lt;script&gt;</div>')

    def test_escape_block(self):
        dangerous = '<script>'
        tag = div(Block('b')(dangerous))
        rendered = str(tag)
        self.assertEqual(rendered, '<div>&lt;script&gt;</div>')

    def test_callable(self):
        tag = html(
            body(
                'a',
                Block('b')('placeholder'),
                'c'
            )
        )
        tag['b'] = lambda ctx:'content'
        rendered = str(tag)
        self.assertEqual(rendered, '<html><body>acontentc</body></html>')

    def test_context(self):
        def greet_user(ctx):
            name = ctx.get('name', 'user')
            return 'Hello %s' % name
        tag = div(
            greet_user
        )

        rendered = str(tag)
        self.assertEqual(rendered, '<div>Hello user</div>')

        rendered = tag.render(name='Cenk')
        self.assertEqual(rendered, '<div>Hello Cenk</div>')

    def test_context_in_block(self):
        def greet_user(ctx):
            name = ctx.get('name', 'user')
            return 'Hello %s' % name
        tag = div(
            Block('b')
        )
        tag['b'] = greet_user

        rendered = tag.render(name='Cenk')
        self.assertEqual(rendered, '<div>Hello Cenk</div>')

    def test_unicode_content(self):
        t = title(u'Türkçe')
        rendered = t.render()
        expected = u'<title>Türkçe</title>'
        self.assertEqual(rendered.decode('utf-8'), expected)

    def test_unicode_attr_value(self):
        t = title(a=u'Türkçe')
        rendered = t.render()
        expected = u'<title a="Türkçe"></title>'
        self.assertEqual(rendered.decode('utf-8'), expected)

    def test_self_closing_tag_init(self):
        t = hr(id=3)
        self.assertEqualWS(str(t), '<hr id="3"/>')

    def test_tag_indent(self):
        f = lambda c: 'text'
        g = lambda c: 'text with\nnewlines'
        t = html(
            head(title('title')),
            body(
                f,
                'some text',
                p('a paragraph'),
                div('div with\nsome\nnewlines'),
                'block start',
                Block('b')(
                    f,
                    'some more text'
                ),
                'block end',
                g,
                div(
                    pre('asdf\nzxcv\nqwerty')
                )
            )
        )
        self.assertEqualWS(str(t), """<html>
  <head>
    <title>
      title
    </title>
  </head>
  <body>
    text
    some text
    <p>
      a paragraph
    </p>
    <div>
      div with
      some
      newlines
    </div>
    block start
    text
    some more text
    block end
    text with
    newlines
    <div>
      <pre>asdf
zxcv
qwerty</pre>
    </div>
  </body>
</html>""")

    def test_block(self):
        f = lambda ctx: 'callable'
        b = Block('b')(
            'text',
            f,
            div(),
        )
        self.assertEqualWS(str(b), """text
callable
<div></div>""")


if __name__ == "__main__":
    unittest.main()
