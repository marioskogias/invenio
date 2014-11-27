from backend import ElasticSearchWrapper


def index_record(sender, recid):
    """
    Index a given record.

    Used to connect to signal.

    :param recid: [int] recid to index
    """
    from .tasks import index_records
    return index_records.delay(sender, recid)


def create_index(sender):
    """
    Create elasticsearch index
    Configure mappings as found in mapping.cfg
    """
    from flask import current_app
    es = current_app.extensions.get("elasticsearch")
    es.create_index()


def setup_app(app):
    """Set up the extension for the given app."""
    from es_query import process_es_query, process_es_results
    es = ElasticSearchWrapper(app)
    es.set_query_handler(process_es_query)
    es.set_results_handler(process_es_results)

    packages = app.extensions["registry"]["packages"]
    packages.register("invenio.ext.elasticsearch")
    from invenio.base import signals
    signals.record_after_create.connect(index_record)
