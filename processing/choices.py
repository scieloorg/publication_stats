# coding: utf-8
import json
import codecs
import os

iso_3166_division = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'iso_3166_divisions.json')
)

iso_3166_country_code = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'iso_3166_country_code.json')
)

ISO_3166_DIVISION_CODE = {}
with codecs.open(iso_3166_division) as divisions:

    for country, divisions in json.loads(divisions.read()).items():
        for division, name in divisions.items():
            div_code = u'%s-%s' % (country, division)
            ISO_3166_DIVISION_CODE[div_code] = name


ISO_3166_COUNTRY_CODE = {}
with codecs.open(iso_3166_country_code) as countries:
    ISO_3166_COUNTRY_CODE = json.loads(countries.read())

ISO_3166_COUNTRY_NAME_AS_KEY = {value.upper(): key for key, value in ISO_3166_COUNTRY_CODE.items()}
ISO_3166_DIVISION_NAME_AS_KEY = {value.upper(): key for key, value in ISO_3166_DIVISION_CODE.items()}
