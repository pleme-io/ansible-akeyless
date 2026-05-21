# OpenAPI coverage matrix

Generated: `2026-05-21T17:01:33Z`

Source spec: `/home/drzzln/code/github/pleme-io/akeyless-go/api/openapi.yaml`

## Summary

| Metric | Value |
|---|---|
| Total operationIds | 604 |
| Covered by an Ansible module | 378 (62.6%) |
| Explicitly skipped (`skip.yml`) | 226 |
| Not yet classified | 0 |
| **Effective coverage** | **604 / 604 (100.0%)** |

## Skip categories

| Category | Count |
|---|---|
| `deprecated` | 110 |
| `future_phase` | 74 |
| `internal_only` | 42 |

## Uncovered operationIds

| operationId | Category | Reason |
|---|---|---|
| `CertificateDiscovery` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `Connect` | `internal_only` | SDK helper invoked transparently by the module helper; not a user-facing module. |
| `CreateESM` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `CreatePasskey` | `internal_only` | Passkey enrollment is per-user interactive flow. |
| `CreateUSC` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `ExportClassicKey` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `GatewayUpdateLdapAuthConfig` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `GatewayUpdateTlsCert` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `GetPKICertificate` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `KubeconfigGenerate` | `internal_only` | Kubernetes cluster auth helper; for kubectl/CSI use, not Ansible. |
| `UpdateClassicKeyCertificate` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `aliasDetails` | `future_phase` | Alias management; deferred. |
| `assocTargetItem` | `future_phase` | Association helper; covered by role_assoc / role_rule for the common cases. |
| `auth` | `internal_only` | SDK helper invoked transparently by the module helper; not a user-facing module. |
| `authMethodDelete` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `authMethodGet` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `authMethodList` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `calcPasswordSecurityInfo` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `changeAdminAccountPassword` | `internal_only` | Admin account password change; security-critical, not for automation. |
| `configure` | `internal_only` | SDK helper invoked transparently by the module helper; not a user-facing module. |
| `createAWSTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createArtifactoryTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethod` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethodAWSIAM` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethodAzureAD` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethodCert` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethodEmail` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethodGCP` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethodK8S` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethodLDAP` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethodOAuth2` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethodOCI` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethodOIDC` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethodSAML` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAuthMethodUniversalIdentity` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createAzureTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createDBTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createDockerhubTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createDynamicSecret` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createEKSTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createEventForwarder` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createGKETarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createGcpTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createGithubTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createGitlabTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createGlobalSignAtlasTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createGlobalSignTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createGodaddyTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createHashiVaultTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createKey` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createLinkedTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createNativeK8STarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createPingTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createRabbitMQTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createRotatedSecret` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createSSHTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createSalesforceTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createUserEvent` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createWebTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createWindowsTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createZeroSSLTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `createldapTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form (e.g. targetCreateAws). |
| `deactivateAcmeAccount` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `decryptGPG` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `decryptPKCS1` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `decryptWithClassicKey` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `deleteAuthMethods` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `deleteEventForwarder` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `deleteGatewayAllowedAccessId` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `deleteGwCluster` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `deleteItems` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `deleteRoles` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `deleteTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `deleteTargetAssociation` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `deleteTargets` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `describeAssoc` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `describePermissions` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `describeSubClaims` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `detokenize` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `detokenizeBatch` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `dynamicSecretGetValue` | `future_phase` | Read-time secret retrieval; deferred to a future *_value lookup plugin. |
| `dynamicSecretTmpCredsDelete` | `internal_only` | Temporary credentials / users; ephemeral, not declarative. |
| `dynamicSecretTmpCredsGet` | `internal_only` | Temporary credentials / users; ephemeral, not declarative. |
| `dynamicSecretTmpCredsUpdate` | `internal_only` | Temporary credentials / users; ephemeral, not declarative. |
| `encryptGPG` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `encryptWithClassicKey` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `eventAction` | `future_phase` | Event subsystem read endpoint; covered when the event_forwarder modules expand. |
| `eventForwarderGet` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `gatewayCreateProducerChef` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `gatewayDownloadCustomerFragments` | `internal_only` | Gateway introspection endpoint; not a configurable resource. |
| `gatewayGetCache` | `internal_only` | Gateway introspection endpoint; not a configurable resource. |
| `gatewayGetConfig` | `internal_only` | Gateway introspection endpoint; not a configurable resource. |
| `gatewayGetDefaults` | `internal_only` | Gateway introspection endpoint; not a configurable resource. |
| `gatewayGetLdapAuthConfig` | `internal_only` | Gateway introspection endpoint; not a configurable resource. |
| `gatewayGetRemoteAccess` | `internal_only` | Gateway introspection endpoint; not a configurable resource. |
| `gatewayGetTmpUsers` | `internal_only` | Gateway introspection endpoint; not a configurable resource. |
| `gatewayMigratePersonalItems` | `future_phase` | Bulk migration endpoint; deferred to dedicated migration tooling. |
| `gatewayRevokeTmpUsers` | `internal_only` | Temporary credentials / users; ephemeral, not declarative. |
| `gatewayStartProducer` | `internal_only` | Gateway lifecycle/runtime control; out of band of declarative config. |
| `gatewayStatusMigration` | `future_phase` | Bulk migration endpoint; deferred to dedicated migration tooling. |
| `gatewayStopProducer` | `internal_only` | Gateway lifecycle/runtime control; out of band of declarative config. |
| `gatewaySyncMigration` | `future_phase` | Bulk migration endpoint; deferred to dedicated migration tooling. |
| `gatewayUpdateCache` | `internal_only` | Gateway runtime override; not a declarative resource. |
| `gatewayUpdateDefaults` | `internal_only` | Gateway runtime override; not a declarative resource. |
| `gatewayUpdateItem` | `internal_only` | Gateway runtime override; not a declarative resource. |
| `gatewayUpdateProducerChef` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `gatewayUpdateRemoteAccess` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gatewayUpdateRemoteAccessDesktopApp` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gatewayUpdateRemoteAccessRdpRecordings` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gatewayUpdateTmpUsers` | `internal_only` | Temporary credentials / users; ephemeral, not declarative. |
| `generateAcmeEab` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `getAccountLogo` | `internal_only` | Branding asset upload; UI-only. |
| `getAccountSettings` | `internal_only` | Account-level settings managed via console. |
| `getAnalyticsData` | `deprecated` | Legacy operationId; superseded by the resource-prefixed *_get form. |
| `getDynamicSecretValue` | `deprecated` | Legacy operationId; superseded by the resource-prefixed *_get form. |
| `getKubeExecCreds` | `internal_only` | Kubernetes cluster auth helper; for kubectl/CSI use, not Ansible. |
| `getLastUserEventStatus` | `deprecated` | Legacy operationId; superseded by the resource-prefixed *_get form. |
| `getRSAPublic` | `deprecated` | Legacy operationId; superseded by the resource-prefixed *_get form. |
| `getRotatedSecretValue` | `deprecated` | Legacy operationId; superseded by the resource-prefixed *_get form. |
| `getSSHCertificate` | `deprecated` | Legacy operationId; superseded by the resource-prefixed *_get form. |
| `getTags` | `deprecated` | Legacy operationId; superseded by the resource-prefixed *_get form. |
| `getTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed *_get form. |
| `getTargetDetails` | `deprecated` | Legacy operationId; superseded by the resource-prefixed *_get form. |
| `gwUpdateRemoteAccessSessionLogsAwsS3` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gwUpdateRemoteAccessSessionLogsAzureAnalytics` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gwUpdateRemoteAccessSessionLogsDatadog` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gwUpdateRemoteAccessSessionLogsElasticsearch` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gwUpdateRemoteAccessSessionLogsGoogleChronicle` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gwUpdateRemoteAccessSessionLogsLogstash` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gwUpdateRemoteAccessSessionLogsLogzIo` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gwUpdateRemoteAccessSessionLogsSplunk` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gwUpdateRemoteAccessSessionLogsStdout` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gwUpdateRemoteAccessSessionLogsSumologic` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `gwUpdateRemoteAccessSessionLogsSyslog` | `internal_only` | Remote-access daemon config; managed via Gateway UI. |
| `importPasswords` | `future_phase` | Bulk migration endpoint; deferred to dedicated migration tooling. |
| `kmipClientDeleteRule` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `kmipClientSetRule` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `kmipMoveServer` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `kmipRenewClientCertificate` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `kmipRenewServerCertificate` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `kmipSetServerState` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `listAcmeAccounts` | `deprecated` | Legacy operationId; superseded by the resource-prefixed *_list form. |
| `listSRASessions` | `internal_only` | Secure Remote Access (SRA) operation; managed via Akeyless console, not Ansible. |
| `listSharedItems` | `deprecated` | Legacy operationId; superseded by the resource-prefixed *_list form. |
| `moveObjects` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `rawCreds` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `refreshKey` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `requestAccess` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `resetAccessKey` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `reverseRBAC` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `revoke-creds` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `rollbackSecret` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `rotateKey` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `rotateOidcClientSecret` | `future_phase` | Rotation trigger; deferred to *_rotate action. |
| `rotateSecret` | `future_phase` | Rotation trigger; deferred to *_rotate action. |
| `rotatedSecretDelete` | `future_phase` | Rotation trigger; deferred to *_rotate action. |
| `rotatedSecretGetValue` | `future_phase` | Read-time secret retrieval; deferred to a future *_value lookup plugin. |
| `setItemState` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `shareItem` | `future_phase` | Sharing flows; deferred. |
| `signGPG` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `signPKICertWithClassicKey` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `signRsaSsaPss` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `staticCredsAuth` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `staticSecretDeleteSync` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `staticSecretSync` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `targetGetDetails` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `tokenize` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `tokenizeBatch` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `unwrapToken` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `updateAWSTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAWSTargetDetails` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAccountSettings` | `internal_only` | Account-level settings managed via console. |
| `updateArtifactoryTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAssoc` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAuthMethodAWSIAM` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAuthMethodAzureAD` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAuthMethodCert` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAuthMethodGCP` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAuthMethodK8S` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAuthMethodLDAP` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAuthMethodOAuth2` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAuthMethodOCI` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAuthMethodOIDC` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAuthMethodSAML` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAuthMethodUniversalIdentity` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateAzureTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateDBTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateDBTargetDetails` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateDockerhubTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateEKSTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateEventForwarder` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateGKETarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateGcpTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateGithubTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateGitlabTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateGlobalSignAtlasTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateGlobalSignTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateGodaddyTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateHashiVaultTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateLdapTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateLdapTargetDetails` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateLinkedTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateNativeK8STarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updatePingTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateRDPTargetDetails` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateRabbitMQTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateRabbitMQTargetDetails` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateRotatedSecret` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateRotationSettings` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateSSHTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateSSHTargetDetails` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateSalesforceTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateTargetDetails` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateWebTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateWebTargetDetails` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateWindowsTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `updateZeroSSLTarget` | `deprecated` | Legacy operationId; superseded by the resource-prefixed form. |
| `uploadRSA` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `validateToken` | `future_phase` | Validation RPC; deferred. |
| `vaultAddress` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `verifyDataWithClassicKey` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `verifyGPG` | `future_phase` | Endpoint not yet wrapped; safe to defer until needed. |
| `verifyJWTWithClassicKey` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `verifyPKICertWithClassicKey` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |
| `verifyRsaSsaPss` | `future_phase` | Specialized crypto/RPC variant; covered by the base action modules. Add a dedicated wrapper when needed. |

