# Copyright (c) 2013 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from marconi import storage
from marconi.tests.util import suite


class Driver(storage.DriverBase):

    @property
    def queue_controller(self):
        return QueueController(self)

    @property
    def message_controller(self):
        pass

    @property
    def claim_controller(self):
        pass


class QueueController(storage.QueueBase):

    def list(self, tenant=None):
        super(QueueController, self).list(tenant)

    def get(self, name, tenant=None):
        super(QueueController, self).get(name, tenant=tenant)

    def create(self, name, tenant=None, ttl=None, **metadata):
        super(QueueController, self).create(name, tenant=tenant,
                                            ttl=ttl, **metadata)

    def update(self, name, tenant=None, **metadata):
        super(QueueController, self).update(name, tenant=tenant, **metadata)

    def delete(self, name, tenant=None):
        super(QueueController, self).delete(name, tenant=tenant)

    def stats(self, name, tenant=None):
        super(QueueController, self).stats(name, tenant=tenant)

    def actions(self, name, tenant=None, marker=None, limit=10):
        super(QueueController, self).actions(name, tenant=tenant,
                                             marker=marker, limit=limit)


class TestQueueBase(suite.TestSuite):

    def setUp(self):
        super(TestQueueBase, self).setUp()
        self.driver = Driver()
        self.controller = self.driver.queue_controller

    def test_create(self):
        self.assertRaises(AssertionError, self.controller.create,
                          "test", ttl=30)

        self.assertRaises(AssertionError, self.controller.create,
                          "test", ttl=1209601)

        self.assertIsNone(self.controller.create("test", ttl=60))
        self.assertIsNone(self.controller.create("test", ttl=120))
        self.assertIsNone(self.controller.create("test", ttl=1209600))
