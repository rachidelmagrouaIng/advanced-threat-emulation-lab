# Hardening and retest notes

Apply changes to a test scope first. Record the original configuration, expected effect, service dependencies and rollback method. The following are engineering notes, not an automated production baseline.

## Active Directory and Windows

- Enable the DNS client policy **Turn off multicast name resolution**, then verify it reached the intended computers. Separately address NetBIOS over TCP/IP where it is unnecessary. LLMNR and NetBIOS are distinct controls.
- Require SMB signing where supported and verify the effective client/server configuration. SMB signing mitigates relay to SMB; it does not eliminate every NTLM relay path, especially paths to other services.
- Audit NTLM usage before restricting it. Prefer Kerberos where supported and review privileged account exposure and local administrator membership.
- Evaluate LDAP signing and LDAP channel binding for their respective connection paths. LDAPS encryption alone does not prove protection against authentication relay.
- Review DHCPv6, router advertisements and WPAD according to the actual network design. Do not blanket-disable IPv6 as a universal fix. Verify legitimate connectivity after a change.
- Restrict WMI administrative access to designated management paths. Correlate process creation and authentication evidence rather than treating all WMI use as malicious.

## Ubuntu and the web application

**SQL injection:** bind user values through parameterized database APIs. Input validation helps business correctness but is not a replacement for separating data from SQL. Give the application only the database access it needs.

**Uploads:** an extension allowlist alone is insufficient. Validate the expected content type, enforce limits, generate server-side filenames and store files outside executable web paths. Configure serving so that an uploaded file cannot become a PHP program.

**SSH:** validate a non-root key-authenticated session and recovery access before changing settings. A lab baseline can include:

```text
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
```

Confirm the effective configuration, including `Match` blocks and distribution includes. Use `sshd -t` before reload and `sshd -T` to inspect effective defaults. `MaxAuthTries` is a per-connection limit; it is not an aggregate rate limiter. Fail2Ban can add temporary source blocking but requires correct log selection, thresholds and recovery procedures.

## Retest acceptance

Each change should meet both conditions: the previously demonstrated path fails under the same preconditions, and expected service use still succeeds. Keep time-aligned logs. Record outcomes as **verified**, **inconclusive** or **not run**, with evidence supporting that label.

## Authoritative references

- [Microsoft: SMB signing](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing-overview)
- [Microsoft: IPv6 configuration guidance](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/configure-ipv6-in-windows)
- [OWASP: SQL injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP: file upload security](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [OpenSSH: sshd_config](https://man.openbsd.org/sshd_config)

- [Microsoft: LDAP signing and channel binding](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/ldap-signing)
