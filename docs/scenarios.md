# Attack paths and defensive validation

These are authorized lab scenarios. This repository documents the security reasoning and retest requirements; it does not include credentials, captured challenge-response material or executable exploitation workflows.

ATT&CK mappings are analytical annotations. Confirm applicability from the actual procedure and telemetry rather than matching an alert title alone.

| Scenario | Lab observation / enabling condition | Defensive control | Retest and evidence to collect | ATT&CK mapping |
| --- | --- | --- | --- | --- |
| LLMNR / NBT-NS poisoning | Fallback name resolution allowed a rogue response and NTLM challenge-response capture | Disable unneeded fallback resolution; verify DNS and client policy application | Packet capture for UDP 5355/137; applied policy; repeat a controlled unresolved-name request | T1557.001 |
| Offline password recovery | Weak credentials exposed by captured NTLM challenge-response material | Strong unique credentials, privileged account separation, reduce NTLM exposure | Document capture conditions and password-policy changes without retaining secret material publicly | T1110.002 |
| SMB relay | A relayed authentication reached a target that did not require signing | Require SMB signing on applicable peers; reduce NTLM; restrict local administrator rights | Verify effective signing requirements and confirm the same SMB relay path fails | T1557.001 |
| IPv6-related authentication redirection | Rogue IPv6 services enabled authentication redirection toward directory services | Review DHCPv6/RA protections, WPAD need, LDAP signing and LDAPS channel binding | Capture rogue service behavior; inspect directory authentication and binding events; verify legitimate name resolution | T1557 (parent mapping; exact sub-technique depends on procedure) |
| WMI remote execution | Valid credentials enabled remote commands on a Windows endpoint | Restrict remote management and privileged accounts; monitor WMI and process lineage | Correlate account logon, WMI activity and target process creation | T1047 |
| SQL injection | A PHP login parameter influenced a SQLite query and exposed table enumeration | Parameterized queries, least-privilege application access, logging | Repeat the affected endpoint test; confirm valid login and absence of unintended query behavior | T1190 when the application is externally reachable; otherwise document local exploit context |
| Executable file upload | Uploaded PHP executed through the web server as its service identity | Store outside web root, prevent execution, validate type and size, randomize names | Confirm a disallowed upload cannot execute; verify intended file features still work | T1505.003 for the web shell stage |
| SSH password attack | Repeated password attempts targeted weak authentication | Key authentication, root-login restriction, access limits and Fail2Ban | Review authentication events; verify authorized key access and expected enforcement | T1110.001 |

## Evidence boundaries

The project demonstrates the attack paths and associated hardening work qualitatively. A single successful demonstration does not establish general coverage. For each retest, keep the host baseline, tool version, timestamp, configuration difference and expected outcome. Do not label a proposed control as verified without a fresh test.

CALDERA is an orchestration layer: a successful agent task is evidence of execution, not proof that the defender detected it. Record an operation identifier, ability identifiers, affected test hosts, command outcome, matching telemetry and cleanup confirmation in a private lab record.

## ATT&CK references

- [Name resolution poisoning and SMB relay](https://attack.mitre.org/techniques/T1557/001/)
- [WMI](https://attack.mitre.org/techniques/T1047/)
- [Password guessing](https://attack.mitre.org/techniques/T1110/001/)
- [Web shell](https://attack.mitre.org/techniques/T1505/003/)
