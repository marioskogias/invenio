mapping = {
    'records': {
        'properties': {
            '_collections': {
                'index': 'not_analyzed',
                'type': 'string'
            },
            '_first_author': {
                'properties': {
                    'first_name': {
                        'fields': {
                            'first_name': {
                                'index': 'analyzed',
                                'type': 'string'
                            },
                            'raw': {
                                'index': 'not_analyzed',
                                'type': 'string'
                            }
                        },
                        'type': 'multi_field'
                    },
                    'full_name': {
                        'fields': {
                            'full_name': {
                                'index': 'analyzed',
                                'type': 'string'
                            },
                            'raw': {
                                'index': 'not_analyzed',
                                'type': 'string'
                            }
                        },
                        'type': 'multi_field'
                    },
                    'last_name': {
                        'fields': {
                            'last_name': {
                                'index': 'analyzed',
                                'type': 'string'
                            },
                            'raw': {
                                'index': 'not_analyzed',
                                'type': 'string'
                            }
                        },
                        'type': 'multi_field'
                    },
                    'name_variations': {
                        'index': 'not_analyzed',
                        'type': 'string'
                    }
                },
                'type': 'object'
            },
            'abstract': {
                    'type': 'object'
            },
            'authors': {
                    'properties': {
                        'first_name': {
                            'fields': {
                                'first_name': {
                                    'index': 'analyzed',
                                    'type': 'string'
                                },
                                'raw': {
                                    'index': 'not_analyzed',
                                    'type': 'string'
                                }
                            },
                            'type': 'multi_field'
                        },
                        'full_name': {
                            'fields': {
                                'full_name': {
                                    'index': 'analyzed',
                                    'type': 'string'
                                },
                                'raw': {
                                    'index': 'not_analyzed',
                                    'type': 'string'
                                }
                            },
                            'type': 'multi_field'
                        },
                        'last_name': {
                            'fields': {
                                'last_name': {
                                    'index': 'analyzed',
                                    'type': 'string'
                                },
                                'raw': {
                                    'index': 'not_analyzed',
                                    'type': 'string'
                                }
                            },
                            'type': 'multi_field'
                        },
                        'name_variations': {
                            'index': 'not_analyzed',
                            'type': 'string'
                        }
                    },
                    'type': 'object'
            },
            'creation_date': {
                    'type': 'date'
            },
            'documents': {
                    'include_in_all': False,
                    'properties': {
                        'file_name': {
                            'index': 'analyzed',
                            'type': 'integer'
                        },
                        'fulltext': {
                            'index': 'analyzed',
                            'type': 'string'
                        }
                    },
                    'type': 'nested'
            },
            'files': {
                    'type': 'nested'
            },
            'keywords': {
                    'type': 'object'
            },
            'modification_date': {
                    'type': 'date'
            },
            'primary_report_number': {
                'index': 'not_analyzed',
                'type': 'string'
            },
            'recid': {
                    'type': 'integer'
            },
            'reference': {
                    'type': 'object'
            },
            'report_number': {
                    'properties': {
                        'report_number': {
                            'index': 'not_analyzed',
                            'type': 'string'
                        }
                    },
                    'type': 'object'
            },
            'title': {
                'properties': {
                    'title': {
                        'fields': {
                            'raw': {
                                'index': 'not_analyzed',
                                'type': 'string'
                            },
                            'title': {
                                'index': 'analyzed',
                                'type': 'string'
                            }
                        },
                        'type': 'multi_field'
                    }
                },
                'type': 'object'
            }
        }
    }
}

highlight = {'fields': {'abstract': {}}}

facets = {
    'Author': {
        'terms': {
            'field': '_first_author.full_name.raw',
            'size': 0
            }
        },
        'Collections': {
            'terms': {
                'field': '_collections',
                'size': 0
                }
            },
       # 'Year': {
       #     'terms': {
       #         'field': 'year',
       #         'size': 0
       #         }
       #     }
        }
