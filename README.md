# tools

Small scripts for common chores.

| Script | What it does | Needs |
|---|---|---|
| [`clean_key.sh`](#clean_keysh) | Replaces a host's stale SSH key in `~/.ssh/known_hosts` | `ssh`, `ssh-keygen`, `host` |
| [`make_cert.sh`](#make_certsh) | Creates an RSA key, CSR and self-signed certificate | `openssl` |
| [`mk_passwd.py`](#mk_passwdpy) | Generates secure random passwords, tokens and passphrases | Python 3.6+ |

## clean_key.sh

Use this when a host has been rebuilt and SSH refuses to connect because its key changed. It removes the host's entries from `~/.ssh/known_hosts`, then connects once to record the new key.

```
$ ./clean_key.sh web01.example.com
Removing web01.example.com
```

> **Warning:** the reconnect uses `StrictHostKeyChecking=no`, so it accepts whatever key the host presents without checking it. Only run this when you know why the key changed.

## make_cert.sh

Creates a 4096-bit RSA key, a certificate signing request (CSR) and a self-signed certificate valid for 365 days. `-c` sets the name of the output directory and files. `openssl` then prompts for the certificate fields, including the common name, so enter the same value there.

```
$ ./make_cert.sh -c example.com
```

The output goes into a directory named after the common name:

| File | Contents |
|---|---|
| `example.com.secure.key` | Private key used to sign the CSR |
| `example.com.key` | Copy of the private key, used to sign the certificate |
| `example.com.csr` | Certificate signing request |
| `example.com.crt` | Self-signed certificate |

Neither key file is passphrase-protected, so keep both private.

## mk_passwd.py

Generates cryptographically secure random strings with Python's `secrets` module. It has three output styles: random characters (the default), readable groups of characters, and word passphrases.

```
$ ./mk_passwd.py                  # 32 random characters
Fv%,6Nked_`s~_FQGzBN_F:p`.e$$flr
$ ./mk_passwd.py -r -l 16         # readable
CQgu-Rf5n-RBzm-VJU9
$ ./mk_passwd.py -p               # passphrase
confound-rasping-moneyless-recoup-borrowing-affirm
```

Run `./mk_passwd.py -h` for the full option list. Warnings and errors go to stderr, so `PW=$(./mk_passwd.py)` captures only the password. The script warns when the estimated strength is below 64 bits of entropy.

### Random characters

By default each string contains at least one lowercase letter, uppercase letter, digit and special character. The characters `\/[]{}()` are left out of the default special set because they often need escaping.

| Option | Effect |
|---|---|
| `-l, --length N` | Characters per string (default 32) |
| `-n, --count N` | Number of strings (default 1) |
| `-S, --no-special` | Letters and digits only |
| `-U`, `-L`, `-D` | Leave out uppercase, lowercase or digits |
| `--special-chars CHARS` | Use exactly these special characters |
| `-x, --exclude CHARS` | Remove these characters from the output |
| `-A, --no-ambiguous` | Remove characters that are easy to misread, such as `0`/`O` and `1`/`l`/`I` |
| `--hex` | Lowercase hex only, for tokens and keys |
| `--no-require-each` | Don't require one character of each enabled type |
| `-v, --verbose` | Print the character-set size and estimated entropy to stderr |

```
./mk_passwd.py -l 64 -S                     # 64 letters and digits
./mk_passwd.py -x '$`"'\''' -n 5              # 5 passwords without shell-hostile characters
./mk_passwd.py --special-chars '!@#-_' -A   # limited special set, nothing easy to misread
./mk_passwd.py -l 40 --hex                  # 40-character hex token
```

A value that starts with `-` must be attached with `=`, for example `--special-chars=-_.` or `-x=-abc`. Otherwise it is read as another option.

### Readable

`-r, --readable` produces output that is easy to read aloud or type from a screen. It removes look-alike characters and special characters, and splits the result into dash-separated groups of 4.

| Option | Effect |
|---|---|
| `-g, --group N` | Group size; `0` turns grouping off. Also works without `-r` |
| `--separator CHAR` | Character between groups (default `-`) |

`--length` counts only the random characters, so `-r -l 16` prints 19 characters including the dashes. To keep some special characters, list them with `--special-chars`.

### Passphrases

`-p, --passphrase` joins random words instead of characters. The default of 6 words is about 77 bits of entropy, roughly as strong as a random 13-character password. The character options and `--length` don't apply in this mode.

| Option | Effect |
|---|---|
| `-w, --words N` | Number of words (default 6) |
| `--separator CHAR` | Character between words (default `-`) |
| `-C, --capitalize` | Capitalize each word |
| `--with-number` | Add one random digit to one word |
| `--wordlist PATH` | Use your own list, one word per line |

```
$ ./mk_passwd.py -p -w 5 -C --with-number --separator .
Unison.Camping.Unleveled.Company3.Posting
```

`-C` and `--with-number` help when a password policy requires uppercase letters or digits.

The default wordlist, `wordlists/eff_large_wordlist.txt`, is the [EFF Large Wordlist](https://www.eff.org/dice) by the Electronic Frontier Foundation, licensed under [CC BY 3.0 US](https://creativecommons.org/licenses/by/3.0/us/). The script looks for `wordlists/` next to itself, so copy that directory along with the script.
