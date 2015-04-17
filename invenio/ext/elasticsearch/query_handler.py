"""This file is responsible for formating the elasticsearch query using the
   invenio_query_parser
"""
from invenio_query_parser.contrib.spires.walkers import spires_to_invenio
from invenio_query_parser.contrib.spires import converter
from invenio_query_parser.ast import AndOp
from invenio.modules.search.walkers.elasticsearch import ElasticSearchDSL
from invenio.modules.search.enhancers import facet_filter, collection_filter
from invenio.base.globals import cfg
from config import es_config
from config import query_mapping
from pypeg2 import *
from six import iteritems

CONFIGURED_FACETS = ["_collections", "_first_author.full_name.raw"]

class QueryHandler(object):

    def __init__(self):
        self.astCreator = converter.SpiresToInvenioSyntaxConverter()
        self.spires_to_invenio_walker = spires_to_invenio.SpiresToInvenio()
        self.dslCreator = ElasticSearchDSL()

    def get_dsl_query(self, query):
        dsl_query = query.accept(self.dslCreator)
        return dsl_query

    def get_query_ast(self, query):
        if query == "*":  # this is what the UI returns FIXME
            query = ""
        ast = self.astCreator.parse_query(query)
        new_ast = ast.accept(self.spires_to_invenio_walker)
        return new_ast

    def enhance_query(self):

        res = self.query

        # Apply the facet filters
        self.format_facet_filters()

        filter_data = facet_filter.get_groupped_facets(self.facet_filters)
        new_nodes = facet_filter.format_facet_tree_nodes(filter_data,
                                                         CONFIGURED_FACETS)
        if new_nodes:
            res = AndOp(new_nodes, self.query)

        # Apply the collection restriction filters
        from invenio.modules.collections.cache import restricted_collection_cache
        from flask_login import current_user as user_info
        policy = cfg['CFG_WEBSEARCH_VIEWRESTRCOLL_POLICY'].strip().upper()
        restricted_cols = restricted_collection_cache.cache
        permitted_restricted_cols = user_info.get('precached_permitted_\
            restricted_collections', [])
        current_col = cfg['CFG_SITE_NAME']
        collection_tree = collection_filter.create_collection_query(\
                restricted_cols, permitted_restricted_cols,
                current_col, policy)

        if collection_tree:
            res = AndOp(collection_tree, res)
        return res

    def format_facet_filters(self):
        facet_list = []
        for item in self.facet_filters:
            for k,v in iteritems(item):
                real_key = es_config.get_records_facets_config().get(k, None)
                if real_key:
                    facet_list.append(['+', real_key['terms']['field'], v])
        self.facet_filters = facet_list


    def format_query(self, query):

        dsl_query = {"query": query}

        # apply aggegation for facets
        dsl_query["aggs"] = es_config.get_records_facets_config()
        dsl_query["highlight"] = es_config.get_records_highlights_config()
        dsl_query["_source"] = es_config.should_return_source
        return dsl_query

    def process_query(self, query, facet_filters):
        self._query = query
        self.facet_filters = facet_filters

        self.query = self.get_query_ast(query)

        enhanced_query = self.enhance_query()
        with open("/root/invenio.log", 'a') as f:
            f.write(str(enhanced_query))
            f.write("\n")
        dsl_query = self.get_dsl_query(enhanced_query)
        return self.format_query(dsl_query)
