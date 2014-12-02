from invenio_query_parser.walkers.pypeg_to_ast import PypegConverter
from invenio_query_parser.walkers.ast_to_dsl import ASTtoDSLConverter
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
           In the future full text as well
        """
        return "records"


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
        return dsl_query


    def process_results(self, results):
        return results
