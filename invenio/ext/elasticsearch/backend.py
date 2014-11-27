from werkzeug.utils import cached_property
from pyelasticsearch import ElasticSearch as PyElasticSearch
import json
from search_logic import QueryHandler


class ElasticSearchWrapper(object):

    def __init__(self, app=None):
        """Build the extension object."""
        self.app = app

        #default process functions
        self.process_query = lambda x: x
        self.process_results = lambda x: x

        # TODO: to put in config?
        self.records_doc_type = "records"
        self.documents_doc_type = "documents"
        self.collections_doc_type = "collections"

        # to cache recids collections
        self._recids_collections = {}

        # initiate the query handler
        self.query_handler = QueryHandler()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize a Flask application.

        Only one Registry per application is allowed.
        """
        app.config.setdefault('ELASTICSEARCH_URL',
                              'http://188.184.141.134:9200/')
        app.config.setdefault('ELASTICSEARCH_INDEX', "invenio_test")
        app.config.setdefault('ELASTICSEARCH_NUMBER_OF_SHARDS', 1)
        app.config.setdefault('ELASTICSEARCH_NUMBER_OF_REPLICAS', 0)
        app.config.setdefault('ELASTICSEARCH_DATE_DETECTION', False)
        app.config.setdefault('ELASTICSEARCH_NUMERIC_DETECTION', False)
        app.config.setdefault('ELASTICSEARCH_ANALYSIS', {
            "default": {"type": "simple"}})
        # Follow the Flask guidelines on usage of app.extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'elasticsearch' in app.extensions:
            raise Exception("Flask application already initialized")

        app.extensions['elasticsearch'] = self
        self.app = app

    @cached_property
    def connection(self):
        """Return a pyelasticsearch connection object."""
        return PyElasticSearch(self.app.config['ELASTICSEARCH_URL'])

    def set_query_handler(self, handler):
        """
        Specify a function to convert the invenio query into a ES query.

        :param handler: [function] take a query[string] parameter
        """
        self.process_query = handler

    def set_results_handler(self, handler):
        """
        Set a function to process the search results.

        To convert ES search results into an object understandable by Invenio.

        :param handler: [function] take a query[string] parameter
        """
        self.process_results = handler

    @property
    def status(self):
        """The status of the ES cluster.
        :return: [string] possible values: green, yellow, red. green means all
          ok including replication, yellow means replication not active, red
          means partial results.
        """
        return self.connection.health().get("status")

    def index_exists(self, index=None):
        """Check if the index exists in the cluster.

        :param index: [string] index name

        :return: [bool] True if exists
        """
        if index is None:
            index = self.app.config['ELASTICSEARCH_INDEX']
        if self.connection.status().get("indices").get(index):
            return True
        return False

    def delete_index(self, index=None):
        """Delete the given index.

        :param index: [string] index name

        :return: [bool] True if success
        """
        if index is None:
            index = self.app.config['ELASTICSEARCH_INDEX']
        try:
            self.connection.delete_index(index=index)
            return True
        except:
            return False

    def create_index(self, index=None):
        if index is None:
            index = self.app.config['ELASTICSEARCH_INDEX']
        if self.index_exists(index=index):
            return True
        try:
            #create index
            index_settings = {
                #should be set to 1 for exact facet count
                "number_of_shards":
                self.app.config['ELASTICSEARCH_NUMBER_OF_SHARDS'],

                #in case of primary shard failed
                "number_of_replicas":
                self.app.config['ELASTICSEARCH_NUMBER_OF_REPLICAS'],

                #disable automatic type detection
                #that can cause errors depending of the indexing order
                "date_detection":
                self.app.config['ELASTICSEARCH_DATE_DETECTION'],
                "numeric_detection":
                self.app.config['ELASTICSEARCH_NUMERIC_DETECTION']
            }
            if self.app.config['ELASTICSEARCH_ANALYSIS']:
                index_settings["analysis"] = \
                    self.app.config['ELASTICSEARCH_ANALYSIS']

            self.connection.create_index(index=index, settings=index_settings)

            #create mappings for each type

            #mapping for records
            self.create_mapping(index, self.records_doc_type)
            return True
        except:
            raise
            return False

    def create_mapping(self, index, doc_type):
        from invenio.ext.elasticsearch.config import mapping
        mapping_cfg = mapping.mappings
        try:
            type_mapping = {str(doc_type): mapping_cfg.get(doc_type)}
        except KeyError:
            print "No such doc_type in cfg"
            return False
        try:
            self.connection.put_mapping(index=index, doc_type=doc_type,
                                        mapping=type_mapping)
        except:
            return False
        return True

    def _bulk_index_docs(self, docs, doc_type, index):
        if not docs:
            return []
        self.app.logger.info("Indexing: %d records for %s" % (len(docs),
                             doc_type))
        refresh_flag = self.app.config.get("DEBUG")
        results = self.connection.bulk_index(index=index,
                                             doc_type=doc_type, docs=docs,
                                             id_field='_id',
                                             refresh=refresh_flag)
        errors = []
        #for it in results.get("items"):
        #    if it.get("index").get("error"):
        #        errors.append((it.get("index").get("_id"),
        #                       it.get("index").get("error")))
        return errors

    def _get_record(self, recid):
        from invenio.modules.records.api import get_record
        record_as_dict = get_record(recid, reset_cache=True).dumps()
        del record_as_dict["__meta_metadata__"]
        #del record_as_dict["_id"]
        #FIXME handle mutliple collection types
        collections = [val.values()[0]
                       for val in record_as_dict["collections"]]
        return record_as_dict

    def index_records(self, recids, index=None, bulk_size=100000, **kwargs):
        """Index bibliographic records.

        The document structure is provided by JsonAlchemy.

        Note: the __metadata__ is removed for the moment.

        TODO: is should be renamed as index?

        :param recids: [list of int] recids to index
        :param index: [string] index name
        :param bulk_size: [int] batch size to index

        :return: [list] list of recids not indexed due to errors
        """
        if index is None:
            index = self.app.config['ELASTICSEARCH_INDEX']
        return self._index_docs(recids, self.records_doc_type, index,
                                bulk_size, self._get_record)

    def _index_docs(self, recids, doc_type, index, bulk_size, get_docs):
        docs = []
        errors = []
        for recid in recids:
            doc = get_docs(recid)
            if doc:
                docs.append(doc)
            if len(docs) >= bulk_size:
                errors += self._bulk_index_docs(docs, doc_type=doc_type,
                                                index=index)
                docs = []
        errors += self._bulk_index_docs(docs, doc_type=doc_type, index=index)
        return errors

    def search(self, query, index=None, filters=None):
        """ query: the users' query
            index: where to search
            filters: a dictionary of filters eg {"collections": "ARTICLE"}
        """
        # Create the elasticsearch query
        dsl_query = self.query_handler.get_dsl_query(query)

        # format query and apply filters eg collections
        dsl_query = self.query_handler.format_query(dsl_query, filters)

        # based on query define where to search, eg full text or records
        doc_type = self.query_handler.get_doc_type(query)

        resuls = self.connection.search(query, index=index, doc_type=doc_type)

        view_results = self.query_handler.process_results(results)

        return view_results
