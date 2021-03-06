# Copyright (c) 2013 Rackspace, Inc.
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

import falcon

from marconi.transport import helpers


class Resource(object):

    __slots__ = ('queue_ctrl')

    def __init__(self, queue_controller):
        self.queue_ctrl = queue_controller

    def on_get(self, req, resp, tenant_id, queue_name):
        resp_dict = self.queue_ctrl.stats(queue_name,
                                          tenant=tenant_id)

        resp.content_location = req.path
        resp.body = helpers.to_json(resp_dict)
        resp.status = falcon.HTTP_200
