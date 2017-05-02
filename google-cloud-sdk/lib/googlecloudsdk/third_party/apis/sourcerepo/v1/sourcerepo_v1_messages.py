"""Generated message classes for sourcerepo version v1.

Access source code repositories hosted by Google.
"""
# NOTE: This file is autogenerated and should not be edited by hand.

from apitools.base.protorpclite import messages as _messages
from apitools.base.py import encoding


package = 'sourcerepo'


class AuditConfig(_messages.Message):
  """Specifies the audit configuration for a service. The configuration
  determines which permission types are logged, and what identities, if any,
  are exempted from logging. An AuditConfig must have one or more
  AuditLogConfigs.  If there are AuditConfigs for both `allServices` and a
  specific service, the union of the two AuditConfigs is used for that
  service: the log_types specified in each AuditConfig are enabled, and the
  exempted_members in each AuditConfig are exempted.  Example Policy with
  multiple AuditConfigs:      {       "audit_configs": [         {
  "service": "allServices"           "audit_log_configs": [             {
  "log_type": "DATA_READ",               "exempted_members": [
  "user:foo@gmail.com"               ]             },             {
  "log_type": "DATA_WRITE",             },             {
  "log_type": "ADMIN_READ",             }           ]         },         {
  "service": "fooservice.googleapis.com"           "audit_log_configs": [
  {               "log_type": "DATA_READ",             },             {
  "log_type": "DATA_WRITE",               "exempted_members": [
  "user:bar@gmail.com"               ]             }           ]         }
  ]     }  For fooservice, this policy enables DATA_READ, DATA_WRITE and
  ADMIN_READ logging. It also exempts foo@gmail.com from DATA_READ logging,
  and bar@gmail.com from DATA_WRITE logging.

  Fields:
    auditLogConfigs: The configuration for logging of each type of permission.
      Next ID: 4
    exemptedMembers: A string attribute.
    service: Specifies a service that will be enabled for audit logging. For
      example, `storage.googleapis.com`, `cloudsql.googleapis.com`.
      `allServices` is a special value that covers all services.
  """

  auditLogConfigs = _messages.MessageField('AuditLogConfig', 1, repeated=True)
  exemptedMembers = _messages.StringField(2, repeated=True)
  service = _messages.StringField(3)


class AuditLogConfig(_messages.Message):
  """Provides the configuration for logging a type of permissions. Example:
  {       "audit_log_configs": [         {           "log_type": "DATA_READ",
  "exempted_members": [             "user:foo@gmail.com"           ]
  },         {           "log_type": "DATA_WRITE",         }       ]     }
  This enables 'DATA_READ' and 'DATA_WRITE' logging, while exempting
  foo@gmail.com from DATA_READ logging.

  Enums:
    LogTypeValueValuesEnum: The log type that this config enables.

  Fields:
    exemptedMembers: Specifies the identities that do not cause logging for
      this type of permission. Follows the same format of Binding.members.
    logType: The log type that this config enables.
  """

  class LogTypeValueValuesEnum(_messages.Enum):
    """The log type that this config enables.

    Values:
      LOG_TYPE_UNSPECIFIED: Default case. Should never be this.
      ADMIN_READ: Admin reads. Example: CloudIAM getIamPolicy
      DATA_WRITE: Data writes. Example: CloudSQL Users create
      DATA_READ: Data reads. Example: CloudSQL Users list
    """
    LOG_TYPE_UNSPECIFIED = 0
    ADMIN_READ = 1
    DATA_WRITE = 2
    DATA_READ = 3

  exemptedMembers = _messages.StringField(1, repeated=True)
  logType = _messages.EnumField('LogTypeValueValuesEnum', 2)


class Binding(_messages.Message):
  """Associates `members` with a `role`.

  Fields:
    members: Specifies the identities requesting access for a Cloud Platform
      resource. `members` can have the following values:  * `allUsers`: A
      special identifier that represents anyone who is    on the internet;
      with or without a Google account.  * `allAuthenticatedUsers`: A special
      identifier that represents anyone    who is authenticated with a Google
      account or a service account.  * `user:{emailid}`: An email address that
      represents a specific Google    account. For example, `alice@gmail.com`
      or `joe@example.com`.   * `serviceAccount:{emailid}`: An email address
      that represents a service    account. For example, `my-other-
      app@appspot.gserviceaccount.com`.  * `group:{emailid}`: An email address
      that represents a Google group.    For example, `admins@example.com`.  *
      `domain:{domain}`: A Google Apps domain name that represents all the
      users of that domain. For example, `google.com` or `example.com`.
    role: Role that is assigned to `members`. For example, `roles/viewer`,
      `roles/editor`, or `roles/owner`. Required
  """

  members = _messages.StringField(1, repeated=True)
  role = _messages.StringField(2)


class CloudAuditOptions(_messages.Message):
  """Write a Cloud Audit log"""


class Condition(_messages.Message):
  """A condition to be met.

  Enums:
    IamValueValuesEnum: Trusted attributes supplied by the IAM system.
    OpValueValuesEnum: An operator to apply the subject with.
    SysValueValuesEnum: Trusted attributes supplied by any service that owns
      resources and uses the IAM system for access control.

  Fields:
    iam: Trusted attributes supplied by the IAM system.
    op: An operator to apply the subject with.
    svc: Trusted attributes discharged by the service.
    sys: Trusted attributes supplied by any service that owns resources and
      uses the IAM system for access control.
    value: DEPRECATED. Use 'values' instead.
    values: The objects of the condition. This is mutually exclusive with
      'value'.
  """

  class IamValueValuesEnum(_messages.Enum):
    """Trusted attributes supplied by the IAM system.

    Values:
      NO_ATTR: Default non-attribute.
      AUTHORITY: Either principal or (if present) authority selector.
      ATTRIBUTION: The principal (even if an authority selector is present),
        which must only be used for attribution, not authorization.
      APPROVER: An approver (distinct from the requester) that has authorized
        this request. When used with IN, the condition indicates that one of
        the approvers associated with the request matches the specified
        principal, or is a member of the specified group. Approvers can only
        grant additional access, and are thus only used in a strictly positive
        context (e.g. ALLOW/IN or DENY/NOT_IN). See: go/rpc-security-policy-
        dynamicauth.
      JUSTIFICATION_TYPE: What types of justifications have been supplied with
        this request. String values should match enum names from
        tech.iam.JustificationType, e.g. "MANUAL_STRING". It is not permitted
        to grant access based on the *absence* of a justification, so
        justification conditions can only be used in a "positive" context
        (e.g., ALLOW/IN or DENY/NOT_IN).  Multiple justifications, e.g., a
        Buganizer ID and a manually-entered reason, are normal and supported.
    """
    NO_ATTR = 0
    AUTHORITY = 1
    ATTRIBUTION = 2
    APPROVER = 3
    JUSTIFICATION_TYPE = 4

  class OpValueValuesEnum(_messages.Enum):
    """An operator to apply the subject with.

    Values:
      NO_OP: Default no-op.
      EQUALS: DEPRECATED. Use IN instead.
      NOT_EQUALS: DEPRECATED. Use NOT_IN instead.
      IN: The condition is true if the subject (or any element of it if it is
        a set) matches any of the supplied values.
      NOT_IN: The condition is true if the subject (or every element of it if
        it is a set) matches none of the supplied values.
      DISCHARGED: Subject is discharged
    """
    NO_OP = 0
    EQUALS = 1
    NOT_EQUALS = 2
    IN = 3
    NOT_IN = 4
    DISCHARGED = 5

  class SysValueValuesEnum(_messages.Enum):
    """Trusted attributes supplied by any service that owns resources and uses
    the IAM system for access control.

    Values:
      NO_ATTR: Default non-attribute type
      REGION: Region of the resource
      SERVICE: Service name
      NAME: Resource name
      IP: IP address of the caller
    """
    NO_ATTR = 0
    REGION = 1
    SERVICE = 2
    NAME = 3
    IP = 4

  iam = _messages.EnumField('IamValueValuesEnum', 1)
  op = _messages.EnumField('OpValueValuesEnum', 2)
  svc = _messages.StringField(3)
  sys = _messages.EnumField('SysValueValuesEnum', 4)
  value = _messages.StringField(5)
  values = _messages.StringField(6, repeated=True)


class CounterOptions(_messages.Message):
  """Options for counters

  Fields:
    field: The field value to attribute.
    metric: The metric to update.
  """

  field = _messages.StringField(1)
  metric = _messages.StringField(2)


class DataAccessOptions(_messages.Message):
  """Write a Data Access (Gin) log"""


class Empty(_messages.Message):
  """A generic empty message that you can re-use to avoid defining duplicated
  empty messages in your APIs. A typical example is to use it as the request
  or the response type of an API method. For instance:      service Foo {
  rpc Bar(google.protobuf.Empty) returns (google.protobuf.Empty);     }  The
  JSON representation for `Empty` is empty JSON object `{}`.
  """



class ListReposResponse(_messages.Message):
  """Response for ListRepos.

  Fields:
    repos: The listed repos.
  """

  repos = _messages.MessageField('Repo', 1, repeated=True)


class LogConfig(_messages.Message):
  """Specifies what kind of log the caller must write

  Fields:
    cloudAudit: Cloud audit options.
    counter: Counter options.
    dataAccess: Data access options.
  """

  cloudAudit = _messages.MessageField('CloudAuditOptions', 1)
  counter = _messages.MessageField('CounterOptions', 2)
  dataAccess = _messages.MessageField('DataAccessOptions', 3)


class MirrorConfig(_messages.Message):
  """Configuration to automatically mirror a repository from another hosting
  service, for example GitHub or BitBucket.

  Fields:
    deployKeyId: ID of the SSH deploy key at the other hosting service.
      Removing this key from the other service would deauthorize Google Cloud
      Source Repositories from mirroring.
    url: URL of the main repository at the other hosting service.
    webhookId: ID of the webhook listening to updates to trigger mirroring.
      Removing this webook from the other hosting service will stop Google
      Cloud Source Repositories from receiving notifications, and thereby
      disabling mirroring.
  """

  deployKeyId = _messages.StringField(1)
  url = _messages.StringField(2)
  webhookId = _messages.StringField(3)


class Policy(_messages.Message):
  """Defines an Identity and Access Management (IAM) policy. It is used to
  specify access control policies for Cloud Platform resources.   A `Policy`
  consists of a list of `bindings`. A `Binding` binds a list of `members` to a
  `role`, where the members can be user accounts, Google groups, Google
  domains, and service accounts. A `role` is a named list of permissions
  defined by IAM.  **Example**      {       "bindings": [         {
  "role": "roles/owner",           "members": [
  "user:mike@example.com",             "group:admins@example.com",
  "domain:google.com",             "serviceAccount:my-other-
  app@appspot.gserviceaccount.com",           ]         },         {
  "role": "roles/viewer",           "members": ["user:sean@example.com"]
  }       ]     }  For a description of IAM and its features, see the [IAM
  developer's guide](https://cloud.google.com/iam).

  Fields:
    auditConfigs: Specifies cloud audit logging configuration for this policy.
    bindings: Associates a list of `members` to a `role`. Multiple `bindings`
      must not be specified for the same `role`. `bindings` with no members
      will result in an error.
    etag: `etag` is used for optimistic concurrency control as a way to help
      prevent simultaneous updates of a policy from overwriting each other. It
      is strongly suggested that systems make use of the `etag` in the read-
      modify-write cycle to perform policy updates in order to avoid race
      conditions: An `etag` is returned in the response to `getIamPolicy`, and
      systems are expected to put that etag in the request to `setIamPolicy`
      to ensure that their change will be applied to the same version of the
      policy.  If no `etag` is provided in the call to `setIamPolicy`, then
      the existing policy is overwritten blindly.
    iamOwned: A boolean attribute.
    rules: If more than one rule is specified, the rules are applied in the
      following manner: - All matching LOG rules are always applied. - If any
      DENY/DENY_WITH_LOG rule matches, permission is denied.   Logging will be
      applied if one or more matching rule requires logging. - Otherwise, if
      any ALLOW/ALLOW_WITH_LOG rule matches, permission is   granted.
      Logging will be applied if one or more matching rule requires logging. -
      Otherwise, if no rule applies, permission is denied.
    version: Version of the `Policy`. The default version is 0.
  """

  auditConfigs = _messages.MessageField('AuditConfig', 1, repeated=True)
  bindings = _messages.MessageField('Binding', 2, repeated=True)
  etag = _messages.BytesField(3)
  iamOwned = _messages.BooleanField(4)
  rules = _messages.MessageField('Rule', 5, repeated=True)
  version = _messages.IntegerField(6, variant=_messages.Variant.INT32)


class Repo(_messages.Message):
  """A repository (or repo) is a Git repository storing versioned source
  content.

  Fields:
    mirrorConfig: How this repository mirrors a repository managed by another
      service.
    name: Resource name of the repository, of the form
      `projects/<project>/repos/<repo>`.
    size: The size in bytes of the repo.
    url: URL to clone the repository from Google Cloud Source Repositories.
  """

  mirrorConfig = _messages.MessageField('MirrorConfig', 1)
  name = _messages.StringField(2)
  size = _messages.IntegerField(3)
  url = _messages.StringField(4)


class Rule(_messages.Message):
  """A rule to be applied in a Policy.

  Enums:
    ActionValueValuesEnum: Required

  Fields:
    action: Required
    conditions: Additional restrictions that must be met
    description: Human-readable description of the rule.
    in_: If one or more 'in' clauses are specified, the rule matches if the
      PRINCIPAL/AUTHORITY_SELECTOR is in at least one of these entries.
    logConfig: The config returned to callers of tech.iam.IAM.CheckPolicy for
      any entries that match the LOG action.
    notIn: If one or more 'not_in' clauses are specified, the rule matches if
      the PRINCIPAL/AUTHORITY_SELECTOR is in none of the entries. The format
      for in and not_in entries is the same as for members in a Binding (see
      google/iam/v1/policy.proto).
    permissions: A permission is a string of form '<service>.<resource
      type>.<verb>' (e.g., 'storage.buckets.list'). A value of '*' matches all
      permissions, and a verb part of '*' (e.g., 'storage.buckets.*') matches
      all verbs.
  """

  class ActionValueValuesEnum(_messages.Enum):
    """Required

    Values:
      NO_ACTION: Default no action.
      ALLOW: Matching 'Entries' grant access.
      ALLOW_WITH_LOG: Matching 'Entries' grant access and the caller promises
        to log the request per the returned log_configs.
      DENY: Matching 'Entries' deny access.
      DENY_WITH_LOG: Matching 'Entries' deny access and the caller promises to
        log the request per the returned log_configs.
      LOG: Matching 'Entries' tell IAM.Check callers to generate logs.
    """
    NO_ACTION = 0
    ALLOW = 1
    ALLOW_WITH_LOG = 2
    DENY = 3
    DENY_WITH_LOG = 4
    LOG = 5

  action = _messages.EnumField('ActionValueValuesEnum', 1)
  conditions = _messages.MessageField('Condition', 2, repeated=True)
  description = _messages.StringField(3)
  in_ = _messages.StringField(4, repeated=True)
  logConfig = _messages.MessageField('LogConfig', 5, repeated=True)
  notIn = _messages.StringField(6, repeated=True)
  permissions = _messages.StringField(7, repeated=True)


class SetIamPolicyRequest(_messages.Message):
  """Request message for `SetIamPolicy` method.

  Fields:
    policy: REQUIRED: The complete policy to be applied to the `resource`. The
      size of the policy is limited to a few 10s of KB. An empty policy is a
      valid policy but certain Cloud Platform services (such as Projects)
      might reject them.
    updateMask: OPTIONAL: A FieldMask specifying which fields of the policy to
      modify. Only the fields in the mask will be modified. If no mask is
      provided, the following default mask is used: paths: "bindings, etag"
      This field is only used by Cloud IAM.
  """

  policy = _messages.MessageField('Policy', 1)
  updateMask = _messages.StringField(2)


class SourcerepoProjectsReposCreateRequest(_messages.Message):
  """A SourcerepoProjectsReposCreateRequest object.

  Fields:
    parent: The project in which to create the repo. Values are of the form
      `projects/<project>`.
    repo: A Repo resource to be passed as the request body.
  """

  parent = _messages.StringField(1, required=True)
  repo = _messages.MessageField('Repo', 2)


class SourcerepoProjectsReposDeleteRequest(_messages.Message):
  """A SourcerepoProjectsReposDeleteRequest object.

  Fields:
    name: The name of the repo to delete. Values are of the form
      `projects/<project>/repos/<repo>`.
  """

  name = _messages.StringField(1, required=True)


class SourcerepoProjectsReposGetIamPolicyRequest(_messages.Message):
  """A SourcerepoProjectsReposGetIamPolicyRequest object.

  Fields:
    resource: REQUIRED: The resource for which the policy is being requested.
      See the operation documentation for the appropriate value for this
      field.
  """

  resource = _messages.StringField(1, required=True)


class SourcerepoProjectsReposGetRequest(_messages.Message):
  """A SourcerepoProjectsReposGetRequest object.

  Fields:
    name: The name of the requested repository. Values are of the form
      `projects/<project>/repos/<repo>`.
  """

  name = _messages.StringField(1, required=True)


class SourcerepoProjectsReposListRequest(_messages.Message):
  """A SourcerepoProjectsReposListRequest object.

  Fields:
    name: The project ID whose repos should be listed. Values are of the form
      `projects/<project>`.
  """

  name = _messages.StringField(1, required=True)


class SourcerepoProjectsReposSetIamPolicyRequest(_messages.Message):
  """A SourcerepoProjectsReposSetIamPolicyRequest object.

  Fields:
    resource: REQUIRED: The resource for which the policy is being specified.
      See the operation documentation for the appropriate value for this
      field.
    setIamPolicyRequest: A SetIamPolicyRequest resource to be passed as the
      request body.
  """

  resource = _messages.StringField(1, required=True)
  setIamPolicyRequest = _messages.MessageField('SetIamPolicyRequest', 2)


class SourcerepoProjectsReposTestIamPermissionsRequest(_messages.Message):
  """A SourcerepoProjectsReposTestIamPermissionsRequest object.

  Fields:
    resource: REQUIRED: The resource for which the policy detail is being
      requested. See the operation documentation for the appropriate value for
      this field.
    testIamPermissionsRequest: A TestIamPermissionsRequest resource to be
      passed as the request body.
  """

  resource = _messages.StringField(1, required=True)
  testIamPermissionsRequest = _messages.MessageField('TestIamPermissionsRequest', 2)


class StandardQueryParameters(_messages.Message):
  """Query parameters accepted by all methods.

  Enums:
    FXgafvValueValuesEnum: V1 error format.
    AltValueValuesEnum: Data format for response.

  Fields:
    f__xgafv: V1 error format.
    access_token: OAuth access token.
    alt: Data format for response.
    bearer_token: OAuth bearer token.
    callback: JSONP
    fields: Selector specifying which fields to include in a partial response.
    key: API key. Your API key identifies your project and provides you with
      API access, quota, and reports. Required unless you provide an OAuth 2.0
      token.
    oauth_token: OAuth 2.0 token for the current user.
    pp: Pretty-print response.
    prettyPrint: Returns response with indentations and line breaks.
    quotaUser: Available to use for quota purposes for server-side
      applications. Can be any arbitrary string assigned to a user, but should
      not exceed 40 characters.
    trace: A tracing token of the form "token:<tokenid>" to include in api
      requests.
    uploadType: Legacy upload protocol for media (e.g. "media", "multipart").
    upload_protocol: Upload protocol for media (e.g. "raw", "multipart").
  """

  class AltValueValuesEnum(_messages.Enum):
    """Data format for response.

    Values:
      json: Responses with Content-Type of application/json
      media: Media download with context-dependent Content-Type
      proto: Responses with Content-Type of application/x-protobuf
    """
    json = 0
    media = 1
    proto = 2

  class FXgafvValueValuesEnum(_messages.Enum):
    """V1 error format.

    Values:
      _1: v1 error format
      _2: v2 error format
    """
    _1 = 0
    _2 = 1

  f__xgafv = _messages.EnumField('FXgafvValueValuesEnum', 1)
  access_token = _messages.StringField(2)
  alt = _messages.EnumField('AltValueValuesEnum', 3, default=u'json')
  bearer_token = _messages.StringField(4)
  callback = _messages.StringField(5)
  fields = _messages.StringField(6)
  key = _messages.StringField(7)
  oauth_token = _messages.StringField(8)
  pp = _messages.BooleanField(9, default=True)
  prettyPrint = _messages.BooleanField(10, default=True)
  quotaUser = _messages.StringField(11)
  trace = _messages.StringField(12)
  uploadType = _messages.StringField(13)
  upload_protocol = _messages.StringField(14)


class TestIamPermissionsRequest(_messages.Message):
  """Request message for `TestIamPermissions` method.

  Fields:
    permissions: The set of permissions to check for the `resource`.
      Permissions with wildcards (such as '*' or 'storage.*') are not allowed.
      For more information see [IAM
      Overview](https://cloud.google.com/iam/docs/overview#permissions).
  """

  permissions = _messages.StringField(1, repeated=True)


class TestIamPermissionsResponse(_messages.Message):
  """Response message for `TestIamPermissions` method.

  Fields:
    permissions: A subset of `TestPermissionsRequest.permissions` that the
      caller is allowed.
  """

  permissions = _messages.StringField(1, repeated=True)


encoding.AddCustomJsonFieldMapping(
    Rule, 'in_', 'in',
    package=u'sourcerepo')
encoding.AddCustomJsonFieldMapping(
    StandardQueryParameters, 'f__xgafv', '$.xgafv',
    package=u'sourcerepo')
encoding.AddCustomJsonEnumMapping(
    StandardQueryParameters.FXgafvValueValuesEnum, '_1', '1',
    package=u'sourcerepo')
encoding.AddCustomJsonEnumMapping(
    StandardQueryParameters.FXgafvValueValuesEnum, '_2', '2',
    package=u'sourcerepo')
