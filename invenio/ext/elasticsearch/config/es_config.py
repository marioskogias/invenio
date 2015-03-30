# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""General config file for ES index."""

from invenio.modules.jsonalchemy.parser import FieldParser
import elasticsearch_cfg as es_cfg
should_return_source = False

################ Fields ###############


def get_records_fields_config():
    """Mapping for records."""
    return es_cfg.mapping


################ Highlights ###############

def get_records_highlights_config():
    """Highlighted fields"""
    return es_cfg.highlight


################ Facets ###############

def get_records_facets_config():
    """Get facets config for records."""
    return es_cfg.facets
