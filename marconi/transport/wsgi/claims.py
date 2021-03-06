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

from marconi.storage import exceptions
from marconi.transport import helpers


class CollectionResource(object):

    __slots__ = ('claim_ctrl')

    def __init__(self, claim_controller):
        self.claim_ctrl = claim_controller

    def on_post(self, req, resp, tenant_id, queue_name):
        if req.content_length is None or req.content_length == 0:
            raise falcon.HTTPBadRequest(_('Bad request'),
                                        _('Missing claim metadata.'))

        #TODO(zyuan): where do we define the limits?
        kwargs = {
            'limit': req.get_param_as_int('limit'),
        }
        kwargs = dict([(k, v) for k, v in kwargs.items() if v is not None])

        try:
            metadata = _filtered(helpers.read_json(req.stream))
            cid, msgs = self.claim_ctrl.create(
                queue_name,
                metadata=metadata,
                tenant=tenant_id,
                **kwargs)
            resp_msgs = list(msgs)

            if len(resp_msgs) != 0:
                for msg in resp_msgs:
                    msg['href'] = _msg_uri_from_claim(
                        req.path.rpartition('/')[0], msg['id'], cid)
                    del msg['id']

                resp.location = req.path + '/' + cid
                resp.body = helpers.to_json(resp_msgs)
                resp.status = falcon.HTTP_200
            else:
                resp.status = falcon.HTTP_204

        except helpers.MalformedJSON:
            raise falcon.HTTPBadRequest(_('Bad request'),
                                        _('Malformed claim metadata.'))

        except exceptions.DoesNotExist:
            raise falcon.HTTPNotFound


class ItemResource(object):

    __slots__ = ('claim_ctrl')

    def __init__(self, claim_controller):
        self.claim_ctrl = claim_controller

    def on_get(self, req, resp, tenant_id, queue_name, claim_id):
        try:
            meta, msgs = self.claim_ctrl.get(
                queue_name,
                claim_id=claim_id,
                tenant=tenant_id)

            meta['messages'] = list(msgs)
            for msg in meta['messages']:
                msg['href'] = _msg_uri_from_claim(
                    req.path.rsplit('/', 2)[0], msg['id'], meta['id'])
                del msg['id']

            meta['href'] = req.path
            del meta['id']

            resp.content_location = req.relative_uri
            resp.body = helpers.to_json(meta)
            resp.status = falcon.HTTP_200

        except exceptions.DoesNotExist:
            raise falcon.HTTPNotFound

    def on_patch(self, req, resp, tenant_id, queue_name, claim_id):
        if req.content_length is None or req.content_length == 0:
            raise falcon.HTTPBadRequest(_('Bad request'),
                                        _('Missing claim metadata.'))

        try:
            metadata = _filtered(helpers.read_json(req.stream))
            self.claim_ctrl.update(queue_name,
                                   claim_id=claim_id,
                                   metadata=metadata,
                                   tenant=tenant_id)

            resp.status = falcon.HTTP_204

        except helpers.MalformedJSON:
            raise falcon.HTTPBadRequest(_('Bad request'),
                                        _('Malformed claim metadata.'))

        except exceptions.DoesNotExist:
            raise falcon.HTTPNotFound

    def on_delete(self, req, resp, tenant_id, queue_name, claim_id):
        self.claim_ctrl.delete(queue_name,
                               claim_id=claim_id,
                               tenant=tenant_id)

        resp.status = falcon.HTTP_204


def _filtered(obj):
    try:
        #TODO(zyuan): verify the TTL
        return {'ttl': obj['ttl']}

    except Exception:
        raise helpers.MalformedJSON


def _msg_uri_from_claim(base_path, msg_id, claim_id):
    return '/'.join(
        [base_path, 'messages', msg_id]
    ) + falcon.to_query_str({'claim_id': claim_id})
