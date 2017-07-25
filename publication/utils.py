# coding: utf-8
import os
import weakref
import re
import unicodedata

from configparser import ConfigParser

REGEX_ISSN = re.compile(r"^[0-9]{4}-[0-9]{3}[0-9xX]$")
TAG_RE = re.compile(r'<[^>]+>')

ELASTICSEARCH_INDEX = os.environ.get('ELASTICSEARCH_INDEX', 'publication')


def remove_tags(text):
    return TAG_RE.sub('', text)


def cleanup_string(text):

    try:
        nfd_form = unicodedata.normalize('NFD', text.strip().lower())
    except TypeError:
        nfd_form = unicodedata.normalize('NFD', unicode(text.strip().lower()))

    cleaned_str = u''.join(x for x in nfd_form if unicodedata.category(x)[0] == 'L' or x == ' ')

    return remove_tags(cleaned_str).lower()


class SingletonMixin(object):
    """
    Adds a singleton behaviour to an existing class.

    weakrefs are used in order to keep a low memory footprint.
    As a result, args and kwargs passed to classes initializers
    must be of weakly refereable types.
    """
    _instances = weakref.WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        key = (cls, args, tuple(kwargs.items()))

        if key in cls._instances:
            return cls._instances[key]

        new_instance = super(type(cls), cls).__new__(cls, *args, **kwargs)
        cls._instances[key] = new_instance

        return new_instance


class Configuration(SingletonMixin):
    """
    Acts as a proxy to the ConfigParser module
    """
    def __init__(self, fp, parser_dep=ConfigParser):
        self.conf = parser_dep()
        self.conf.readfp(fp)

    @classmethod
    def from_env(cls):
        try:
            filepath = os.environ['PUBLICATIONSTATS_SETTINGS_FILE']
        except KeyError:
            raise ValueError('missing env variable PUBLICATIONSTATS_SETTINGS_FILE')

        return cls.from_file(filepath)

    @classmethod
    def from_file(cls, filepath):
        """
        Returns an instance of Configuration

        ``filepath`` is a text string.
        """
        fp = open(filepath, 'r')
        return cls(fp)

    def __getattr__(self, attr):
        return getattr(self.conf, attr)

    def items(self):
        """Settings as key-value pair.
        """
        return [(section, dict(self.conf.items(section, raw=True))) for \
            section in [section for section in self.conf.sections()]]


def ckeck_given_issns(issns):
    valid_issns = []

    for issn in issns:
        if not REGEX_ISSN.match(issn):
            continue
        valid_issns.append(issn)

    return valid_issns
