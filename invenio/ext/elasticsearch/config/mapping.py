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
                "type": "nested",
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
            },
            "_first_author": {
                "type": "nested",
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
        }
    }
}