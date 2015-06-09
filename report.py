#!/usr/bin/env python

from dateutil.parser import parse
from sys import argv
import datetime
import json
import re

from jinja2 import Environment, FileSystemLoader, evalcontextfilter, Markup, escape

def as_datetime(dt_string, format='%Y-%m-%d'):
    dt_datetime = parse(dt_string)
    return dt_datetime.strftime(format)

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', Markup('<br>\n'))
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

with open(argv[1]) as fp:
    json = json.load(fp)

    # Index members for later lookup
    member_by_id = { }
    for member in json['members']:
        member_by_id[member['id']] = member

    # Index the lists for later lookup
    list_by_id = { }
    for list in json['lists']:
        list['cards'] = [ ]
        list_by_id[list['id']] = list

    # To make life easy for the template, for each card: (1) add any checklists to the
    # card itself, (2) add any members to the card itself.
    for card in json['cards']:
        card['checklists'] = [ checklist
                               for checklist in json['checklists']
                               if checklist['id'] in card['idChecklists'] ]
        card['members'] = [ member_by_id[member_id]
                            for member_id in card['idMembers'] ]
        list_by_id[card['idList']]['cards'].append(card)

    env = Environment(loader = FileSystemLoader('.'),
                      trim_blocks = True,
                      lstrip_blocks = True)
    env.filters['datetime'] = as_datetime
    env.filters['nl2br'] = nl2br

    template = env.get_template('trello.jinja2')
    output = template.render(json)

    print output
