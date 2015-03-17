# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Test ElasticSearch indexer engine"""

from invenio.testsuite import InvenioTestCase

class TestElasticSearchEngine(InvenioTestCase):

    def setUp(self):
        """Create an IndexerConfiguration object"""
        from ..indexerext.config import IndexerConfiguration,\
                ElasticSearchIndex, VirtualIndex

        el_index1 = ElasticSearchIndex("field1")
        el_index2 = ElasticSearchIndex("filed2")
        v_index = VirtualIndex("temp_vindex", indices=[el_index1, el_index2])

        self.configuration = IndexerConfiguration([el_index1, el_index2],
                                                  [v_index])


    def test_index_not_found(self):
        print self.configuration.indices
        #for k,v in self.configuration.index_dict.iteritems():
        #    print "%s: %s" % (k, v.name)
        assert True

