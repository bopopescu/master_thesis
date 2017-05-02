# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This package facilitates HTTP/REST requests to the registry."""



import httplib
import json
import re
import threading
import urllib

from containerregistry.client import docker_creds  # pylint: disable=unused-import
from containerregistry.client import docker_name
from containerregistry.client.v2_2 import docker_creds as v2_2_creds
import httplib2  # pylint: disable=unused-import

# Options for docker_http.Transport actions
PULL = 'pull'
PUSH = 'push,pull'
# For now DELETE is PUSH, which is the read/write ACL.
DELETE = PUSH
CATALOG = 'catalog'
ACTIONS = [PULL, PUSH, DELETE, CATALOG]

MANIFEST_SCHEMA1_MIME = 'application/vnd.docker.distribution.manifest.v1+json'
MANIFEST_SCHEMA1_SIGNED_MIME = (
    'application/vnd.docker.distribution.manifest.v1+prettyjws')
MANIFEST_SCHEMA2_MIME = 'application/vnd.docker.distribution.manifest.v2+json'
MANIFEST_LIST_MIME = 'application/vnd.docker.distribution.manifest.list.v2+json'
LAYER_MIME = 'application/vnd.docker.image.rootfs.diff.tar.gzip'
CONFIG_JSON_MIME = 'application/vnd.docker.container.image.v1+json'
MANIFEST_SCHEMA1_MIMES = [MANIFEST_SCHEMA1_MIME, MANIFEST_SCHEMA1_SIGNED_MIME]
MANIFEST_SCHEMA2_MIMES = [MANIFEST_SCHEMA2_MIME]
SUPPORTED_MANIFEST_MIMES = [MANIFEST_SCHEMA1_MIMES, MANIFEST_SCHEMA2_MIME]


class Diagnostic(object):
  """Diagnostic encapsulates a Registry v2 diagnostic message.

  This captures one of the "errors" from a v2 Registry error response
  message, as outlined here:
    https://github.com/docker/distribution/blob/master/docs/spec/api.md#errors

  Args:
    error: the decoded JSON of the "errors" array element.
  """

  def __init__(self, error):
    self._error = error

  def __eq__(self, other):
    return (self.code == other.code and
            self.message == other.message and
            self.detail == other.detail)

  @property
  def code(self):
    return self._error.get('code')

  @property
  def message(self):
    return self._error.get('message')

  @property
  def detail(self):
    return self._error.get('detail')


def _DiagnosticsFromContent(content):
  try:
    o = json.loads(content)
    return [Diagnostic(d) for d in o.get('errors', [])]
  except:
    return [Diagnostic({
        'code': 'UNKNOWN',
        'message': content,
    })]


class V2DiagnosticException(Exception):
  """Exceptions when an unexpected HTTP status is returned."""

  def __init__(
      self,
      resp,
      content):
    self._resp = resp
    self._diagnostics = _DiagnosticsFromContent(content)
    message = '\n'.join(['response: %s' % resp] + [
        '%s: %s' % (d.message, d.detail) for d in self._diagnostics])
    super(V2DiagnosticException, self).__init__(message)

  @property
  def diagnostics(self):
    return self._diagnostics

  @property
  def response(self):
    return self._resp

  @property
  def http_status_code(self):
    if self._resp.status:
      # Check to see if the raw http response was given.
      return self._resp.status
    # Return the 'status' contained in an actual dict.
    return int(self._resp.get('status'))


class BadStateException(Exception):
  """Exceptions when we have entered an unexpected state."""


def _CheckState(
    predicate,
    message=None
):
  if not predicate:
    raise BadStateException(message if message else 'Unknown')


_CHALLENGE = 'Bearer '
_REALM_PFX = 'realm='
_SERVICE_PFX = 'service='


class Transport(object):
  """HTTP Transport abstraction to handle automatic v2 reauthentication.

  In the v2 Registry protocol, all of the API endpoints expect to receive
  'Bearer' authentication.  These Bearer tokens are generated by exchanging
  'Basic' or 'Anonymous' authentication with an authentication endpoint
  designated by the opening ping request.

  The Bearer tokens are scoped to a resource (typically repository), and
  are generated with a set of capabilities embedded (e.g. push, pull).

  The Docker client has a baked in 60-second expiration for Bearer tokens,
  and upon expiration, registries can reject any request with a 401.  The
  transport should automatically refresh the Bearer token and reissue the
  request.

  Args:
     name: the structured name of the docker resource being referenced.
     creds: the basic authentication credentials to use for authentication
            challenge exchanges.
     transport: the HTTP transport to use under the hood.
     action: One of docker_http.ACTIONS, for which we plan to use this transport
  """

  def __init__(
      self,
      name,
      creds,
      transport,
      action):
    self._name = name
    self._basic_creds = creds
    self._transport = transport
    self._action = action
    self._lock = threading.Lock()

    _CheckState(action in ACTIONS,
                'Invalid action supplied to docker_http.Transport: %s' % action)

    # Ping once to establish realm, and then get a good credential
    # for use with this transport.
    self._Ping()
    self._Refresh()

  def _Ping(self):
    """Ping the v2 Registry.

    Only called during transport construction, this pings the listed
    v2 registry.  The point of this ping is to establish the "realm"
    and "service" to use for Basic for Bearer-Token exchanges.
    """
    # This initiates the pull by issuing a v2 ping:
    #   GET H:P/v2/
    headers = {
        'content-type': 'application/json',
        'user-agent': docker_name.USER_AGENT,
    }
    resp, unused_content = self._transport.request(
        '{scheme}://{registry}/v2/'.format(scheme=Scheme(self._name.registry),
                                           registry=self._name.registry),
        'GET',
        body=None,
        headers=headers)

    # We expect a www-authenticate challenge.
    _CheckState(resp.status == httplib.UNAUTHORIZED,
                'Unexpected status: %d' % resp.status)

    challenge = resp['www-authenticate']
    _CheckState(challenge.startswith(_CHALLENGE),
                'Unexpected "www-authenticate" header: %s' % challenge)

    # Default "_service" to the registry
    self._service = self._name.registry

    tokens = challenge[len(_CHALLENGE):].split(',')
    for t in tokens:
      if t.startswith(_REALM_PFX):
        self._realm = t[len(_REALM_PFX):].strip('"')
      elif t.startswith(_SERVICE_PFX):
        self._service = t[len(_SERVICE_PFX):].strip('"')

    # Make sure these got set.
    _CheckState(self._realm, 'Expected a "%s" in "www-authenticate" '
                'header: %s' % (_REALM_PFX, challenge))

  def _Scope(self):
    """Construct the resource scope to pass to a v2 auth endpoint."""
    return self._name.scope(self._action)

  def _Refresh(self):
    """Refreshes the Bearer token credentials underlying this transport.

    This utilizes the "realm" and "service" established during _Ping to
    set up _bearer_creds with up-to-date credentials, by passing the
    client-provided _basic_creds to the authorization realm.

    This is generally called under two circumstances:
      1) When the transport is created (eagerly)
      2) When a request fails on a 401 Unauthorized
    """
    headers = {
        'content-type': 'application/json',
        'user-agent': docker_name.USER_AGENT,
        'Authorization': self._basic_creds.Get()
    }
    parameters = {
        'scope': self._Scope(),
        'service': self._service,
    }
    resp, content = self._transport.request(
        # 'realm' includes scheme and path
        '{realm}?{query}'.format(
            realm=self._realm,
            query=urllib.urlencode(parameters)),
        'GET', body=None, headers=headers)

    _CheckState(resp.status == httplib.OK,
                'Bad status during token exchange: %d\n%s' % (
                    resp.status, content))

    wrapper_object = json.loads(content)
    _CheckState('token' in wrapper_object,
                'Malformed JSON response: %s' % content)

    with self._lock:
      # We have successfully reauthenticated.
      self._bearer_creds = v2_2_creds.Bearer(wrapper_object['token'])

  # pylint: disable=invalid-name
  def Request(
      self,
      url,
      accepted_codes=None,
      method=None,
      body=None,
      content_type=None,
      accepted_mimes=None
  ):
    """Wrapper containing much of the boilerplate REST logic for Registry calls.

    Args:
      url: the URL to which to talk
      accepted_codes: the list of acceptable http status codes
      method: the HTTP method to use (defaults to GET/PUT depending on
              whether body is provided)
      body: the body to pass into the PUT request (or None for GET)
      content_type: the mime-type of the request (or None for JSON).
              content_type is ignored when body is None.
      accepted_mimes: the list of acceptable mime-types

    Raises:
      BadStateException: an unexpected internal state has been encountered.
      V2DiagnosticException: an error has occured interacting with v2.

    Returns:
      The response of the HTTP request, and its contents.
    """
    if not method:
      method = 'GET' if not body else 'PUT'

    # If the first request fails on a 401 Unauthorized, then refresh the
    # Bearer token and retry.
    for retry in [True, False]:
      # self._bearer_creds may be changed by self._Refresh(), so do
      # not hoist this.
      headers = {
          'Authorization': self._bearer_creds.Get(),
          'user-agent': docker_name.USER_AGENT,
      }

      if body:  # Requests w/ bodies should have content-type.
        headers['content-type'] = (content_type if content_type else
                                   'application/json')

      if accepted_mimes is not None:
        headers['Accept'] = ','.join(accepted_mimes)

      # POST/PUT require a content-length, when no body is supplied.
      if method in ('POST', 'PUT') and not body:
        headers['content-length'] = '0'

      resp, content = self._transport.request(
          url, method, body=body, headers=headers)

      if resp.status != httplib.UNAUTHORIZED:
        break
      elif retry:
        # On Unauthorized, refresh the credential and retry.
        self._Refresh()

    if resp.status not in accepted_codes:
      # Use the content returned by GCR as the error message.
      raise V2DiagnosticException(resp, content)

    return resp, content

  def PaginatedRequest(
      self,
      url,
      accepted_codes=None,
      method=None,
      body=None,
      content_type=None
  ):
    """Wrapper around Request that follows Link headers if they exist.

    Args:
      url: the URL to which to talk
      accepted_codes: the list of acceptable http status codes
      method: the HTTP method to use (defaults to GET/PUT depending on
              whether body is provided)
      body: the body to pass into the PUT request (or None for GET)
      content_type: the mime-type of the request (or None for JSON)

    Yields:
      The return value of calling Request for each page of results.
    """
    next_page = url

    while next_page:
      resp, content = self.Request(next_page, accepted_codes, method,
                                   body, content_type)
      yield resp, content

      next_page = ParseNextLinkHeader(resp)


def ParseNextLinkHeader(
    resp
):
  """Returns "next" link from RFC 5988 Link header or None if not present."""
  link = resp.get('link')
  if not link:
    return None

  m = re.match(r'.*<(.+)>;\s*rel="next".*', link)
  if not m:
    return None

  return m.group(1)


def Scheme(endpoint):
  """Returns https scheme for all the endpoints except localhost."""
  if endpoint.startswith('localhost:'):
    return 'http'
  else:
    return 'https'
