# Configure the elasticsearch mappings for each type
mappings = {
    "records": {
        "properties": {
            "files": {
                "type": "nested"
            },
            "title": {
                "type": "multi_field",
                "fields": {
                    "title": {
                        "type": "string",
                        "index": "analyzed"
                    },
                    "raw": {
                        "type": "string",
                        "index": "not_analyzed"
                    }
                }
            },
            "collections": {
                "index": "not_analyzed",
                "type": "string"
            },
            "authors": {
                "type": "object",
                "properties": {
                    "first_name": {
                        "type": "multi_field",
                        "fields": {
                            "first_name": {
                                "type": "string",
                                "index": "analyzed"
                            },
                            "raw": {
                                "type": "string",
                                "index": "not_analyzed"
                            }
                        }
                    },
                    "last_name": {
                        "type": "multi_field",
                        "fields": {
                            "last_name": {
                                "type": "string",
                                "index": "analyzed"
                            },
                            "raw": {
                                "type": "string",
                                "index": "not_analyzed"
                            }
                        }
                    },
                    "full_name": {
                        "type": "multi_field",
                        "fields": {
                            "full_name": {
                                "type": "string",
                                "index": "analyzed"
                            },
                            "raw": {
                                "type": "string",
                                "index": "not_analyzed"
                            }
                        }
                    }
                }
            },
            "_first_author": {
                "type": "object",
                "properties": {
                    "first_name": {
                        "type": "multi_field",
                        "fields": {
                            "first_name": {
                                "type": "string",
                                "index": "analyzed"
                            },
                            "raw": {
                                "type": "string",
                                "index": "not_analyzed"
                            }
                        }
                    },
                    "last_name": {
                        "type": "multi_field",
                        "fields": {
                            "last_name": {
                                "type": "string",
                                "index": "analyzed"
                            },
                            "raw": {
                                "type": "string",
                                "index": "not_analyzed"
                            }
                        }
                    },
                    "full_name": {
                        "type": "multi_field",
                        "fields": {
                            "full_name": {
                                "type": "string",
                                "index": "analyzed"
                            },
                            "raw": {
                                "type": "string",
                                "index": "not_analyzed"
                            }
                        }
                    }
                }
            }
        }
    },
    "documents": {
        "_parent": {"type": "records"},
        "properties": {
            "fulltext": {
                "type": "string",
                "index": "analyzed"
                },
            "recid": {
                "type": "integer",
                "index": "not_analyzed"
                }
        }
    }
}

# Configure the aggegations used for UI facets
aggs = {
    "Collections": {
        "terms": {
            "field": "collections"
        }
    },
    "Author Name": {
        "terms": {
            "field": "_first_author.full_name.raw"
        }
    }
}
