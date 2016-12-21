__all__ = [
    'LXMLTreeBuilder',
    'LXMLTreeBuilderForXSD'
    ]

from io import BytesIO
from StringIO import StringIO
import collections
from lxml import etree
from bs4.element import (
    Comment,
    Doctype,
    NamespacedAttribute,
    ProcessingInstruction,
    XMLProcessingInstruction,
)
from bs4.builder import (
    FAST,
    HTML,
    HTMLTreeBuilder,
    PERMISSIVE,
    ParserRejectedMarkup,
    TreeBuilder,
    XSD)
from bs4.dammit import EncodingDetector

LXML = 'lxml'

class LXMLTreeBuilderForXSD(TreeBuilder):
    DEFAULT_PARSER_CLASS = etree.XMLParser

    is_xsd = True

    
    NAME = "lxml-xsd"
    ALTERNATE_NAMES = ["xsd"]

    features = [NAME, LXML, XSD, FAST, PERMISSIVE]

    CHUNK_SIZE = 512

    # This namespace mapping is specified in the XSD Namespace
    DEFAULT_NSMAPS = {'http://www.w3.org/2001/XMLSchema': "xsd"}
    
    is_xml = True

    def default_parser(self, encoding):
        # This can either return a parser object or a class, which
        # will be instantiated with default arguments.
        if self._default_parser is not None:
            return self._default_parser
        return etree.XMLParser(
            target=self, strip_cdata=False, recover=True, encoding=encoding)

    def parser_for(self, encoding):
        # Use the default parser.
        parser = self.default_parser(encoding)

        if isinstance(parser, collections.Callable):
            parser = parser(target=self, strip_cdata=False, encoding=encoding)
        return parser

    def __init__(self, parser=None, empty_element_tags=None):
        self._default_parser = parser
        if empty_element_tags is not None:
            self.empty_element_tags = set(empty_element_tags)
        self.soup = None
        self.nsmaps = [self.DEFAULT_NSMAPS]

    def _getNsTag(self, tag):
        # Split the namespace URL out of a fully-qualified lxml tag
        if tag[0] == '{':
            return tuple(tag[1:].split('}', 1))
        else:
            return (None, tag)

    def prepare_markup(self, markup, user_specified_encoding=None,
                       exclude_encodings=None,
                       document_declared_encoding=None):

        if isinstance(markup, unicode):

            yield markup, None, document_declared_encoding, False

        if isinstance(markup, unicode):
            yield (markup.encode("utf8"), "utf8",
                   document_declared_encoding, False)

        is_html = not self.is_xsd
        if is_html:
            pass
        else:
            self.processing_instruction_class = XMLProcessingInstruction
        try_encodings = [user_specified_encoding, document_declared_encoding]
        detector = EncodingDetector(
            markup, try_encodings, is_html, exclude_encodings)
        for encoding in detector.encodings:
            yield detector.markup, encoding, document_declared_encoding, False

    def feed(self, markup):
        if isinstance(markup, bytes):
            markup = BytesIO(markup)
        elif isinstance(markup, unicode):
            markup = StringIO(markup)

        data = markup.read(self.CHUNK_SIZE)
        try:
            self.parser = self.parser_for(self.soup.original_encoding)
            self.parser.feed(data)
            while len(data) != 0:
                # Now call feed() on the rest of the data, chunk by chunk.
                data = markup.read(self.CHUNK_SIZE)
                if len(data) != 0:
                    self.parser.feed(data)
            self.parser.close()
        except (UnicodeDecodeError, LookupError, etree.ParserError), e:
            raise ParserRejectedMarkup(str(e))

    def close(self):
        self.nsmaps = [self.DEFAULT_NSMAPS]

    def start(self, name, attrs, nsmap={}):
        # Make sure attrs is a mutable dict--lxml may send an immutable dictproxy.
        attrs = dict(attrs)
        nsprefix = None
        # Invert each namespace map as it comes in.
        if len(self.nsmaps) > 1:
            # There are no new namespaces for this tag, but
            # non-default namespaces are in play, so we need a
            # separate tag stack to know when they end.
            self.nsmaps.append(None)
        elif len(nsmap) > 0:
            # A new namespace mapping has come into play.
            inverted_nsmap = dict((value, key) for key, value in nsmap.items())
            self.nsmaps.append(inverted_nsmap)
            # Also treat the namespace mapping as a set of attributes on the
            # tag, so we can recreate it later.
            attrs = attrs.copy()
            for prefix, namespace in nsmap.items():
                attribute = NamespacedAttribute(
                    "xsd", prefix, "http://www.w3.org/2001/XMLSchema")
                attrs[attribute] = namespace

        # Namespaces are in play. Find any attributes that came in
        # from lxml with namespaces attached to their names, and
        # turn then into NamespacedAttribute objects.
        new_attrs = {}
        for attr, value in attrs.items():
            namespace, attr = self._getNsTag(attr)
            if namespace is None:
                new_attrs[attr] = value
            else:
                nsprefix = self._prefix_for_namespace(namespace)
                attr = NamespacedAttribute(nsprefix, attr, namespace)
                new_attrs[attr] = value
        attrs = new_attrs

        namespace, name = self._getNsTag(name)
        nsprefix = self._prefix_for_namespace(namespace)
        self.soup.handle_starttag(name, namespace, nsprefix, attrs)

    def _prefix_for_namespace(self, namespace):
        if namespace is None:
            return None
        for inverted_nsmap in reversed(self.nsmaps):
            if inverted_nsmap is not None and namespace in inverted_nsmap:
                return inverted_nsmap[namespace]
        return None

    def end(self, name):
        self.soup.endData()
        namespace, name = self._getNsTag(name)
        nsprefix = None
        if namespace is not None:
            for inverted_nsmap in reversed(self.nsmaps):
                if inverted_nsmap is not None and namespace in inverted_nsmap:
                    nsprefix = inverted_nsmap[namespace]
                    break
        self.soup.handle_endtag(name, nsprefix)
        if len(self.nsmaps) > 1:
            # This tag, or one of its parents, introduced a namespace
            # mapping, so pop it off the stack.
            self.nsmaps.pop()

    def pi(self, target, data):
        self.soup.endData()
        self.soup.handle_data(target + ' ' + data)
        self.soup.endData(self.processing_instruction_class)

    def data(self, content):
        self.soup.handle_data(content)

    def doctype(self, name, pubid, system):
        self.soup.endData()
        doctype = Doctype.for_name_and_ids(name, pubid, system)
        self.soup.object_was_parsed(doctype)

    def comment(self, content):
        "Handle comments as Comment objects."
        self.soup.endData()
        self.soup.handle_data(content)
        self.soup.endData(Comment)

    def test_fragment_to_document(self, fragment):
        return u'<?xml version="1.0" encoding="utf-8"?>\n%s' % fragment


class LXMLTreeBuilder(HTMLTreeBuilder, LXMLTreeBuilderForXSD):

    NAME = LXML
    ALTERNATE_NAMES = ["lxml-html"]

    features = ALTERNATE_NAMES + [NAME, HTML, FAST, PERMISSIVE]
    processing_instruction_class = ProcessingInstruction
    is_xsd = False
    is_xml = False

    def default_parser(self, encoding):
        return etree.HTMLParser

    def feed(self, markup):
        encoding = self.soup.original_encoding
        try:
            self.parser = self.parser_for(encoding)
            self.parser.feed(markup)
            self.parser.close()
        except (UnicodeDecodeError, LookupError, etree.ParserError), e:
            raise ParserRejectedMarkup(str(e))


    def test_fragment_to_document(self, fragment):
        return u'<html><body>%s</body></html>' % fragment
