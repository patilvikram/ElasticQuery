# ElasticQuery
# File: filter_query.py
# Desc: define structs for ES Filters & Queries

from datetime import datetime


class Filter(object):
    type = 'filter'

    @classmethod
    def nested(self, path, must=None, should=None, must_not=None):
        must = [v[2] for v in must] if isinstance(must, list) else []
        should = [v[2] for v in should] if isinstance(should, list) else []
        must_not = [v[2] for v in must_not] if isinstance(must_not, list) else []

        return self.type, path, {
            'nested': {
                'path': path,
                self.type: {
                    'bool': {
                        'must': must,
                        'should': should,
                        'must_not': must_not
                    }
                }
            }
        }

    @classmethod
    def range(self, field, gt=None, gte=None, lt=None, lte=None):
        data = {
            'range': {
                field: {}
            }
        }
        if gt is not None:
            data['range'][field]['gt'] = gt
        if gte is not None:
            data['range'][field]['gte'] = gte
        if lt is not None:
            data['range'][field]['lt'] = lt
        if lte is not None:
            data['range'][field]['lte'] = lte

        for range_key, range_value in data['range'][field].iteritems():
            if isinstance(range_value, datetime):
                data['range'][field][range_key] = range_value.isoformat()

        return self.type, field, data

    @classmethod
    def prefix(self, **kwargs):
        return self.type, kwargs.keys(), {
            'prefix': kwargs
        }

    @classmethod
    def term(self, **kwargs):
        term_data={}

        if 'boost' in kwargs.keys():
            print 'boost in kwargs'
            field=None
            for key in kwargs.keys():
                if key =='boost':
                    term_data['boost']=kwargs[key]
                else:
                    term_data['value']=kwargs[key]
                    field=key

            temp=term_data
            term_data={}
            term_data[field]=temp
            return self.type, kwargs.keys(), {
                'term': term_data
            }
        else:
            return self.type, kwargs.keys(), {
                'term': kwargs
            }

    @classmethod
    def terms(self, **kwargs):
        return self.type, None, {
            'terms': kwargs
        }

    @classmethod
    def match(self, **kwargs):
        if self.type == 'filter':
            return self.type, kwargs.keys(), {
                'query': {
                    'match': kwargs,
                    'analyzer': None
                }
            }
        else:
            return self.type, kwargs.keys(), {
                'match': kwargs
            }

    @classmethod
    def missing(self, field):
        if self.type == 'filter':
            return self.type, field, {
                'missing': {
                    'field': field
                }
            }
        else:
            return self.type, field, {
                'filtered': {
                    'filter': {
                        'missing': {
                            'field': field
                        }
                    }
                }
            }

    @classmethod
    def raw_string(self, string, default_operator='AND'):
        if self.type == 'filter':
            return self.type, [], {
                'query': {
                    'query_string': {
                        'query': string,
                        'default_operator': default_operator
                    }
                }
            }
        else:
            return self.type, [], {
                'query_string': {
                    'query': string,
                    'default_operator': default_operator
                }
            }

    @classmethod
    def string(self, default_operator='AND', list_operator='OR', **kwargs):
        and_filters = []
        for key, value in kwargs.iteritems():
            if isinstance(value, list):
                if len(value) > 0:
                    or_filters = []
                    for match in value:
                        or_filters.append(u'({0})'.format(match))

                    and_filters.append(u'({0}:({1}))'.format(key, u' {0} '.format(list_operator).join(or_filters)))
            else:
                and_filters.append(u'{0}:{1}'.format(key, value))

        query_string = u' {0} '.format(default_operator).join(and_filters)

        if self.type == 'filter':
            return self.type, [], {
                'query': {
                    'query_string': {
                        'query': query_string,
                        'default_operator': default_operator
                    }
                }
            }
        else:
            return self.type, [], {
                'query_string': {
                    'query': query_string,
                    'default_operator': default_operator
                }
            }

    @classmethod
    def or_filter(self, *args):
        if self.type == 'filter':
            return self.type, [], {
                'or': [arg[2] for arg in args]
            }
        else:
            return self.type, [], {
                'filtered': {
                    'filter': {
                        'or': [arg[2] for arg in args]
                    }
                }
            }


class Query(Filter):
    type = 'query'

    @classmethod
    def mlt(self, field, match, min_term_frequency=1, max_query_terms=False):
        settings = {
            'like_text': match
        }
        if min_term_frequency:
            settings['min_term_freq'] = min_term_frequency
        if max_query_terms:
            settings['max_query_terms'] = max_query_terms

        return self.type, field, {
            'more_like_this_field': {
                field: settings
            }
        }

    @classmethod
    def positive(self, *queries):
        settings = {}
        for type, field, object in queries:
            if len( field )> 0:
                settings.update(object)
        return self.type, ['positive'], settings

    @classmethod
    def negative(self,negative_boost=0.1, negative_query=None):
        settings = {}
        negative_query_result={}
        print negative_query
        for type, field, object in negative_query:
            if len( field )> 0:
                 negative_query_result.update(field)
        return self.type, negative_query_result
