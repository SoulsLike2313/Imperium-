# SSH Matrix With Commentary

Generated from this host using ssh -Q on 2026-05-07 06:27:36 UTC.

Each row maps one SSH algorithm identifier (your 'address') to a plain-language explanation ('who is who').

## cipher

| Address (identifier) | Who is who |
|---|---|
| `3des-cbc` | CBC mode cipher: legacy; avoid unless compatibility is required. |
| `aes128-cbc` | CBC mode cipher: legacy; avoid unless compatibility is required. |
| `aes192-cbc` | CBC mode cipher: legacy; avoid unless compatibility is required. |
| `aes256-cbc` | CBC mode cipher: legacy; avoid unless compatibility is required. |
| `aes128-ctr` | CTR mode cipher: strong and widely compatible. |
| `aes192-ctr` | CTR mode cipher: strong and widely compatible. |
| `aes256-ctr` | CTR mode cipher: strong and widely compatible. |
| `aes128-gcm@openssh.com` | AEAD cipher: modern and preferred (built-in integrity). |
| `aes256-gcm@openssh.com` | AEAD cipher: modern and preferred (built-in integrity). |
| `chacha20-poly1305@openssh.com` | AEAD cipher: modern and preferred (built-in integrity). |

## cipher-auth

| Address (identifier) | Who is who |
|---|---|
| `aes128-gcm@openssh.com` | Authenticated cipher (AEAD): encryption + integrity in one algorithm. |
| `aes256-gcm@openssh.com` | Authenticated cipher (AEAD): encryption + integrity in one algorithm. |
| `chacha20-poly1305@openssh.com` | Authenticated cipher (AEAD): encryption + integrity in one algorithm. |

## compression

| Address (identifier) | Who is who |
|---|---|
| `none` | No compression; safest default for many environments. |
| `zlib@openssh.com` | Delayed zlib compression (after auth); safer than pre-auth compression. |
| `zlib` | Traditional zlib compression; legacy compatibility option. |

## kex

| Address (identifier) | Who is who |
|---|---|
| `diffie-hellman-group1-sha1` | SHA-1 based DH: legacy and weak; avoid when possible. |
| `diffie-hellman-group14-sha1` | SHA-1 based DH: legacy and weak; avoid when possible. |
| `diffie-hellman-group14-sha256` | DH group14 with SHA-256: acceptable compatibility choice. |
| `diffie-hellman-group16-sha512` | Finite-field DH with large groups and SHA-512: strong but heavier. |
| `diffie-hellman-group18-sha512` | Finite-field DH with large groups and SHA-512: strong but heavier. |
| `diffie-hellman-group-exchange-sha1` | SHA-1 based DH: legacy and weak; avoid when possible. |
| `diffie-hellman-group-exchange-sha256` | DH group exchange with SHA-256: compatible, older style. |
| `ecdh-sha2-nistp256` | ECDH over NIST P-curves: secure and common. |
| `ecdh-sha2-nistp384` | ECDH over NIST P-curves: secure and common. |
| `ecdh-sha2-nistp521` | ECDH over NIST P-curves: secure and common. |
| `curve25519-sha256` | Curve25519 key exchange: modern, fast, and strongly recommended. |
| `curve25519-sha256@libssh.org` | Curve25519 key exchange: modern, fast, and strongly recommended. |
| `sntrup761x25519-sha512@openssh.com` | Hybrid post-quantum + X25519 key exchange; modern and strong. |

## kex-gss

| Address (identifier) | Who is who |
|---|---|
| `gss-gex-sha1-` | GSSAPI key exchange using SHA-1; legacy compatibility variant. |
| `gss-group1-sha1-` | GSSAPI key exchange using SHA-1; legacy compatibility variant. |
| `gss-group14-sha1-` | GSSAPI key exchange using SHA-1; legacy compatibility variant. |
| `gss-group14-sha256-` | GSSAPI key exchange variant for Kerberos/SSO environments (modern hash/curve). |
| `gss-group16-sha512-` | GSSAPI key exchange variant for Kerberos/SSO environments (modern hash/curve). |
| `gss-nistp256-sha256-` | GSSAPI key exchange variant for Kerberos/SSO environments (modern hash/curve). |
| `gss-curve25519-sha256-` | GSSAPI key exchange variant for Kerberos/SSO environments (modern hash/curve). |

## key

| Address (identifier) | Who is who |
|---|---|
| `ssh-ed25519` | Ed25519 public key: modern default recommendation. |
| `ssh-ed25519-cert-v01@openssh.com` | Ed25519 key certificate format (OpenSSH CA-signed key). |
| `sk-ssh-ed25519@openssh.com` | Hardware-backed Ed25519 (FIDO/U2F security key). |
| `sk-ssh-ed25519-cert-v01@openssh.com` | CA-signed certificate form of hardware-backed Ed25519 key. |
| `ecdsa-sha2-nistp256` | ECDSA key over NIST curve: secure and widely supported. |
| `ecdsa-sha2-nistp256-cert-v01@openssh.com` | CA-signed certificate form of ECDSA key. |
| `ecdsa-sha2-nistp384` | ECDSA key over NIST curve: secure and widely supported. |
| `ecdsa-sha2-nistp384-cert-v01@openssh.com` | CA-signed certificate form of ECDSA key. |
| `ecdsa-sha2-nistp521` | ECDSA key over NIST curve: secure and widely supported. |
| `ecdsa-sha2-nistp521-cert-v01@openssh.com` | CA-signed certificate form of ECDSA key. |
| `sk-ecdsa-sha2-nistp256@openssh.com` | Hardware-backed ECDSA key (FIDO/U2F token). |
| `sk-ecdsa-sha2-nistp256-cert-v01@openssh.com` | CA-signed certificate form of hardware-backed ECDSA key. |
| `ssh-dss` | DSA key type: obsolete and generally disabled/rejected. |
| `ssh-dss-cert-v01@openssh.com` | DSA key type: obsolete and generally disabled/rejected. |
| `ssh-rsa` | RSA key type label; SHA-1 signatures are legacy, prefer rsa-sha2-* signatures. |
| `ssh-rsa-cert-v01@openssh.com` | RSA key type label; SHA-1 signatures are legacy, prefer rsa-sha2-* signatures. |

## key-cert

| Address (identifier) | Who is who |
|---|---|
| `ssh-ed25519-cert-v01@openssh.com` | OpenSSH certificate (CA-signed) for Ed25519 key. |
| `sk-ssh-ed25519-cert-v01@openssh.com` | OpenSSH certificate (CA-signed) for Ed25519 key. |
| `ecdsa-sha2-nistp256-cert-v01@openssh.com` | OpenSSH certificate for ECDSA key. |
| `ecdsa-sha2-nistp384-cert-v01@openssh.com` | OpenSSH certificate for ECDSA key. |
| `ecdsa-sha2-nistp521-cert-v01@openssh.com` | OpenSSH certificate for ECDSA key. |
| `sk-ecdsa-sha2-nistp256-cert-v01@openssh.com` | OpenSSH certificate for hardware-backed (security key) credential. |
| `ssh-dss-cert-v01@openssh.com` | OpenSSH certificate for obsolete DSA key type. |
| `ssh-rsa-cert-v01@openssh.com` | OpenSSH certificate for RSA key type. |

## key-plain

| Address (identifier) | Who is who |
|---|---|
| `ssh-ed25519` | Raw Ed25519 key (non-certificate). |
| `sk-ssh-ed25519@openssh.com` | Raw hardware-backed Ed25519 key. |
| `ecdsa-sha2-nistp256` | Raw ECDSA key (non-certificate). |
| `ecdsa-sha2-nistp384` | Raw ECDSA key (non-certificate). |
| `ecdsa-sha2-nistp521` | Raw ECDSA key (non-certificate). |
| `sk-ecdsa-sha2-nistp256@openssh.com` | Raw hardware-backed ECDSA key. |
| `ssh-dss` | Raw DSA key (obsolete). |
| `ssh-rsa` | Raw RSA key type. |

## key-sig

| Address (identifier) | Who is who |
|---|---|
| `ssh-ed25519` | Ed25519 signing algorithm (or cert form). |
| `ssh-ed25519-cert-v01@openssh.com` | Ed25519 signing algorithm (or cert form). |
| `sk-ssh-ed25519@openssh.com` | Security-key backed signing algorithm. |
| `sk-ssh-ed25519-cert-v01@openssh.com` | Security-key backed signing algorithm. |
| `ecdsa-sha2-nistp256` | ECDSA signing algorithm (or cert form). |
| `ecdsa-sha2-nistp256-cert-v01@openssh.com` | ECDSA signing algorithm (or cert form). |
| `ecdsa-sha2-nistp384` | ECDSA signing algorithm (or cert form). |
| `ecdsa-sha2-nistp384-cert-v01@openssh.com` | ECDSA signing algorithm (or cert form). |
| `ecdsa-sha2-nistp521` | ECDSA signing algorithm (or cert form). |
| `ecdsa-sha2-nistp521-cert-v01@openssh.com` | ECDSA signing algorithm (or cert form). |
| `sk-ecdsa-sha2-nistp256@openssh.com` | Security-key backed signing algorithm. |
| `sk-ecdsa-sha2-nistp256-cert-v01@openssh.com` | Security-key backed signing algorithm. |
| `webauthn-sk-ecdsa-sha2-nistp256@openssh.com` | WebAuthn/FIDO security-key signature algorithm. |
| `ssh-dss` | Legacy signature label (prefer modern SHA-2 forms for RSA; avoid DSA). |
| `ssh-dss-cert-v01@openssh.com` | Legacy signature label (prefer modern SHA-2 forms for RSA; avoid DSA). |
| `ssh-rsa` | Legacy signature label (prefer modern SHA-2 forms for RSA; avoid DSA). |
| `ssh-rsa-cert-v01@openssh.com` | Legacy signature label (prefer modern SHA-2 forms for RSA; avoid DSA). |
| `rsa-sha2-256` | RSA with SHA-2 signatures: modern RSA signing algorithms. |
| `rsa-sha2-256-cert-v01@openssh.com` | RSA with SHA-2 signatures: modern RSA signing algorithms. |
| `rsa-sha2-512` | RSA with SHA-2 signatures: modern RSA signing algorithms. |
| `rsa-sha2-512-cert-v01@openssh.com` | RSA with SHA-2 signatures: modern RSA signing algorithms. |

## mac

| Address (identifier) | Who is who |
|---|---|
| `hmac-sha1` | SHA-1 based HMAC: legacy compatibility option. |
| `hmac-sha1-96` | SHA-1 based HMAC: legacy compatibility option. |
| `hmac-sha2-256` | HMAC-SHA2 integrity algorithm: strong and recommended. |
| `hmac-sha2-512` | HMAC-SHA2 integrity algorithm: strong and recommended. |
| `hmac-md5` | MD5-based HMAC: obsolete/weak; avoid in new configurations. |
| `hmac-md5-96` | MD5-based HMAC: obsolete/weak; avoid in new configurations. |
| `umac-64@openssh.com` | UMAC integrity algorithm: fast; 128-bit variant is stronger than 64-bit. |
| `umac-128@openssh.com` | UMAC integrity algorithm: fast; 128-bit variant is stronger than 64-bit. |
| `hmac-sha1-etm@openssh.com` | Encrypt-then-MAC mode: preferred MAC construction in non-AEAD modes. |
| `hmac-sha1-96-etm@openssh.com` | Encrypt-then-MAC mode: preferred MAC construction in non-AEAD modes. |
| `hmac-sha2-256-etm@openssh.com` | Encrypt-then-MAC mode: preferred MAC construction in non-AEAD modes. |
| `hmac-sha2-512-etm@openssh.com` | Encrypt-then-MAC mode: preferred MAC construction in non-AEAD modes. |
| `hmac-md5-etm@openssh.com` | Encrypt-then-MAC mode: preferred MAC construction in non-AEAD modes. |
| `hmac-md5-96-etm@openssh.com` | Encrypt-then-MAC mode: preferred MAC construction in non-AEAD modes. |
| `umac-64-etm@openssh.com` | Encrypt-then-MAC mode: preferred MAC construction in non-AEAD modes. |
| `umac-128-etm@openssh.com` | Encrypt-then-MAC mode: preferred MAC construction in non-AEAD modes. |

## protocol-version

| Address (identifier) | Who is who |
|---|---|
| `2` | SSH protocol version 2 (the modern SSH protocol). |

## sig

| Address (identifier) | Who is who |
|---|---|
| `ssh-ed25519` | Ed25519 signature algorithm (modern default choice). |
| `sk-ssh-ed25519@openssh.com` | Security-key (FIDO/U2F) Ed25519 signature algorithm. |
| `ecdsa-sha2-nistp256` | ECDSA signature algorithm over NIST curve. |
| `ecdsa-sha2-nistp384` | ECDSA signature algorithm over NIST curve. |
| `ecdsa-sha2-nistp521` | ECDSA signature algorithm over NIST curve. |
| `sk-ecdsa-sha2-nistp256@openssh.com` | Security-key ECDSA signature algorithm. |
| `webauthn-sk-ecdsa-sha2-nistp256@openssh.com` | WebAuthn-backed security-key signature algorithm. |
| `ssh-dss` | DSA signature algorithm (obsolete). |
| `ssh-rsa` | Legacy RSA signature label; prefer rsa-sha2-256/512. |
| `rsa-sha2-256` | RSA signature algorithm with SHA-2 (modern RSA signatures). |
| `rsa-sha2-512` | RSA signature algorithm with SHA-2 (modern RSA signatures). |

