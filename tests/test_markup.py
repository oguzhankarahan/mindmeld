#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_markup
----------------------------------

Tests for `markup` module.
"""
from __future__ import unicode_literals

import pytest

from mmworkbench import markup

from mmworkbench.core import Entity, QueryEntity, Span

MARKED_UP_STRS = [
    'show me houses under {[600,000|sys:number] dollars|price}',
    'show me houses under {[$600,000|sys:number]|price}',
    'show me houses under {[1.5|sys:number] million dollars|price}',
    'play {s.o.b.|track}',
    "what's on at {[8 p.m.|sys:time]|range}?",
    'is {s.o.b.|show} gonna be on at {[8 p.m.|sys:time]|range}?',
    'this is a {role model|type|role}',
    'this query has no entities'
]

MARKED_DOWN_STRS = [
    'show me houses under 600,000 dollars',
    'show me houses under $600,000',
    'show me houses under 1.5 million dollars',
    'play s.o.b.',
    "what's on at 8 p.m.?",
    'is s.o.b. gonna be on at 8 p.m.?',
    'this is a role model',
    'this query has no entities'
]


@pytest.mark.mark_down
def test_mark_down():
    text = 'is {s.o.b.|show} gonna be on at {[8 p.m.|sys:time]|range}?'
    marked_down = markup.mark_down(text)
    assert marked_down == 'is s.o.b. gonna be on at 8 p.m.?'


@pytest.mark.load
def test_load_basic_query(query_factory):
    markup_text = 'This is a test query string'
    processed_query = markup.load_query(markup_text, query_factory)
    assert processed_query
    assert processed_query.query


@pytest.mark.load
def test_load_entity(query_factory):
    markup_text = 'When does the {Elm Street|store_name} store close?'

    processed_query = markup.load_query(markup_text, query_factory)

    assert len(processed_query.entities) == 1

    entity = processed_query.entities[0]
    assert entity.span.start == 14
    assert entity.span.end == 23
    assert entity.normalized_text == 'elm street'
    assert entity.entity.type == 'store_name'


@pytest.mark.load
@pytest.mark.numeric
@pytest.mark.focus
def test_load_numerics(query_factory):

    text = 'show me houses under {[600,000|sys:number] dollars|price}'
    processed_query = markup.load_query(text, query_factory)

    assert processed_query
    assert len(processed_query.entities) == 1

    entity = processed_query.entities[0]
    assert entity.text == '600,000 dollars'
    assert entity.entity.type == 'price'
    assert entity.span.start == 21


@pytest.mark.load
@pytest.mark.numeric
def test_load_numerics_2(query_factory):
    text = 'show me houses under {[$600,000|sys:number]|price}'
    processed_query = markup.load_query(text, query_factory)
    assert processed_query


@pytest.mark.load
@pytest.mark.numeric
def test_load_numerics_3(query_factory):
    text = 'show me houses under {[1.5|sys:number] million dollars|price}'
    processed_query = markup.load_query(text, query_factory)
    assert processed_query


@pytest.mark.load
@pytest.mark.special
def test_load_special_chars(query_factory):
    text = 'play {s.o.b.|track}'
    # 'play {s o b|track}'
    processed_query = markup.load_query(text, query_factory)
    entities = processed_query.entities

    assert len(entities)
    entity = entities[0]
    assert entity.text == 's.o.b.'
    assert entity.normalized_text == 's o b'
    assert entity.span.start == 5
    assert entity.span.end == 10


@pytest.mark.load
@pytest.mark.special
def test_load_special_chars_2(query_factory):
    text = "what's on {[8 p.m.|sys:time]|range}?"
    processed_query = markup.load_query(text, query_factory)
    entities = processed_query.entities

    assert len(entities)

    assert entities[0].text == '8 p.m.'
    assert entities[0].normalized_text == '8 p m'
    assert entities[0].span == Span(10, 15)


@pytest.mark.load
@pytest.mark.special
def test_load_special_chars_3(query_factory):
    text = 'is {s.o.b.|show} gonna be on at {[8 p.m.|sys:time]|range}?'
    processed_query = markup.load_query(text, query_factory)
    entities = processed_query.entities

    expected = [
        QueryEntity.from_query(processed_query.query, Entity('show'), Span(3, 8)),
        QueryEntity.from_query(processed_query.query, Entity('range'), Span(25, 30)),
    ]
    assert expected == entities


@pytest.mark.load
@pytest.mark.special
def test_load_special_chars_4(query_factory):
    text = 'is {s.o.b.|show} ,, gonna be on at {[8 p.m.|sys:time]|range}?'

    processed_query = markup.load_query(text, query_factory)
    entities = processed_query.entities

    expected = [
        QueryEntity.from_query(processed_query.query, Entity('show'), Span(3, 8)),
        QueryEntity.from_query(processed_query.query, Entity('range'), Span(28, 33)),
    ]
    assert expected == entities


@pytest.mark.load
@pytest.mark.special
def test_load_special_chars_5(query_factory):
    text = 'what christmas movies   are  , showing {[at 8pm|sys:time]|range}'

    processed_query = markup.load_query(text, query_factory)

    assert len(processed_query.entities) == 1

    entity = processed_query.entities[0]

    assert entity.span.start == 39
    assert entity.span.end == 44
    assert entity.normalized_text == 'at 8pm'
