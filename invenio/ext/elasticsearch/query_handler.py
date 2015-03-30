"""This file is responsible for formating the elasticsearch query using the
   invenio_query_parser
"""
from invenio_query_parser.contrib.spires.walkers import spires_to_invenio
from invenio_query_parser.contrib.spires import converter
from invenio.modules.search.walkers.elasticsearch import ElasticSearchDSL
from config import es_config
from config import query_mapping
from pypeg2 import *


class QueryHandler(object):

    def __init__(self):
        self.astCreator = converter.SpiresToInvenioSyntaxConverter()
        self.spires_to_invenio_walker = spires_to_invenio.SpiresToInvenio()
        self.dslCreator = ElasticSearchDSL()

    def get_dsl_query(self, query):
        if query == "*":  # this is what the UI returns FIXME
            return {"match_all": {}}
        ast = self.astCreator.parse_query(query)
        print ast
        new_ast = ast.accept(self.spires_to_invenio_walker)
        print new_ast
        dsl_query = new_ast.accept(self.dslCreator)
        return dsl_query

    def get_permitted_restricted_colleciton(self):
        """Return a tuple of lists
            This first list contains the allowed collections
            Ths second list contains the forbiden collections
        """
        from flask.ext.login import current_user
        allowed_from_restricted = current_user.get("precached_permitted_\
                restricted_collections", [])
        print allowed_from_restricted

        from invenio.modules.collections.cache import \
                restricted_collection_cache
        restricted = restricted_collection_cache.cache
        print restricted

        final_restricted = list(set(restricted) - set(allowed_from_restricted))
        return final_restricted

    def format_collection_filters(self):
        no_cols = self.get_permitted_restricted_colleciton()
        must_not_f = {"_collections": no_cols}
        return must_not_f

    def format_facet_filters(self, facet_filters):
        def _f(ffilter):
            for k,v in ffilter.iteritems():
                real_k = es_config.get_records_facets_config()\
                        .get(k)['terms']['field']
                return {real_k: v}
        return map(_f, facet_filters)

    def format_filters(self, must_f, should_f, must_not_f):
        """Accepts three list of dictionaries
           Each dictionary is a filter
           At first only term filters are supported
        """
        def _handle_filters(x):
            # x is a dictionary with a single key-value pair
            value = x.values()[0]
            if isinstance(value, list):
                if value:
                    return {"terms": x}
                return None
            else:
                return {"term": x}

        must_filters = filter(None, map(_handle_filters, must_f))
        should_filters = filter(None, map(_handle_filters, should_f))
        must_not_filters = filter(None, map(_handle_filters, must_not_f))

        if must_filters or should_filters or must_not_filters:
            res = {"bool":{}}
            if must_filters:
                res["bool"]["must"] = must_filters
            if should_filters:
                res["bool"]["should"] = should_filters
            if must_not_filters:
                res["bool"]["must_not"] = must_not_filters
            return res
        return {}

    def format_query(self, query, user_filters=None):
        # FIXME handle the given filters
        must_not = self.format_collection_filters()
        filters = self.format_filters(user_filters, [], [must_not])

        dsl_query = {"query": query}
        if filters:
            dsl_query = {"query": {
                "filtered": {
                    "query": query,
                    "filter":filters
                    }
                }
            }

        # apply aggegation for facets
        dsl_query["aggs"] = es_config.get_records_facets_config()
        dsl_query["highlight"] = es_config.get_records_highlights_config()
        dsl_query["_source"] = es_config.should_return_source
        return dsl_query

    def process_query(self, query, facet_filters):
        dsl_query = self.get_dsl_query(query)
        facet_filters = self.format_facet_filters(facet_filters)
        return self.format_query(dsl_query, facet_filters)
