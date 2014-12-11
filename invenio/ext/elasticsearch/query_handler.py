from invenio_query_parser.walkers.pypeg_to_ast import PypegConverter
from ast_to_dsl import ASTtoDSLConverter
from invenio_query_parser import parser
from pypeg2 import *


class QueryHandler(object):

    def __init__(self, fields_dict):
        self.astCreator = PypegConverter()
        self.dslCreator = ASTtoDSLConverter(fields_dict)

    def get_dsl_query(self, query):
        peg = parse(query, parser.Main, whitespace="")
        ast = peg.accept(self.astCreator)
        dsl_query = ast.accept(self.dslCreator)
        return dsl_query

    def get_doc_type(self, query):
        """For now on only records
            Do we need more types?
        """
        pass

    def format_query(self, query, filters=None):
        dsl_query = {"query": query}
        if filters:
            dsl_query = {"query": {
                "filtered": {
                    "query": query,
                    "filter": filters
                    }
                }
            }

        # apply aggegation for facets
        dsl_query["aggs"] = {
            "collections": {
                "terms": {
                    "field": "collections"
                 }
            }
        }
        print dsl_query
        return dsl_query

    def process_query(self, query, filters):
        dsl_query = self.get_dsl_query(query)
        return self.format_query(dsl_query, filters)
