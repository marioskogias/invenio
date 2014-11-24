from werkzeug.utils import cached_property
from pyelasticsearch import ElasticSearch as PyElasticSearch


class ElasticSearch(object):

    """
    Flask extension.

    Initialization of the extension:

    >>> from flask import Flask
    >>> from flask_elasticsearch import ElasticSearch
    >>> app = Flask('myapp')
    >>> s = ElasticSearch(app=app)

    or alternatively using the factory pattern:

    >>> app = Flask('myapp')
    >>> s = ElasticSearch()
    >>> s.init_app(app)
    """

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

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize a Flask application.

        Only one Registry per application is allowed.
        """
        app.config.setdefault('ELASTICSEARCH_URL', 'http://localhost:9200/')
        app.config.setdefault('ELASTICSEARCH_INDEX', "invenio")
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

        See: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/cluster-health.html
        for more.

        TODO: is it useful?

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


    def _bulk_index_docs(self, docs, doc_type, index):
        if not docs:
            return []
        self.app.logger.info("Indexing: %d records for %s" % (len(docs),
                             doc_type))
        results = self.connection.bulk_index(index=index,
                                             doc_type=doc_type, docs=docs,
                                             id_field='_id',
                                             refresh=self.app.config.get("DEBUG"))
        errors = []
        for it in results.get("items"):
            if it.get("index").get("error"):
                errors.append((it.get("index").get("_id"), it.get("index").get("error")))
        return errors

    def _get_record(self, recid):
        from invenio.modules.records.api import get_record
        record_as_dict = get_record(recid, reset_cache=True).dumps()
        del record_as_dict["__meta_metadata__"]
        del record_as_dict["_id"]
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

def index_record(sender, recid):
    """
    Index a given record.

    Used to connect to signal.

    :param recid: [int] recid to index
    """
    from .tasks import index_records
    return index_records.delay(sender, recid)

def setup_app(app):
    """Set up the extension for the given app."""
    from es_query import process_es_query, process_es_results
    es = ElasticSearch(app)
    es.set_query_handler(process_es_query)
    es.set_results_handler(process_es_results)

    app.extensions["registry"]["packages"].register("invenio.ext.elasticsearch")
    from invenio.base import signals
    signals.record_after_create.connect(index_record)
