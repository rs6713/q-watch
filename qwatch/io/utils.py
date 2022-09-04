from collections import namedtuple

MovieLabels = namedtuple(
    'MovieLabels', ['name', 'label', 'addit_props'], defaults=[None])
MovieEntries = namedtuple(
    'MovieEntries', ['name', 'table', 'return_properties', 'joins'], defaults=[None, None])
TableAggregate = namedtuple(
    'TableAggregate', ['table_name', 'aggs', 'groups', 'criteria'], defaults=[None]
)
TableJoin = namedtuple(
    'TableJoin', ['table', 'return_properties',
                  'base_table_prop', 'join_table_prop', 'isouter']
)
Aggregate = namedtuple(
    'Aggregate', ['property', 'label', 'func']
)
