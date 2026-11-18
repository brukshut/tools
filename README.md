# tools
Provides some useful scripts for common chores.

## describe_vpcs.rb

This ruby script will scrape your AWS account for vpc and, optionally, subnet information and outputs `terraform` variable maps. These are useful if you are working with an existing AWS infrastructure that is not managed by `terraform` and do not wish to import your existing vpcs or subnets. It requires a region as an argument passed to the `-r` flag. Without any additional arguments, it will map all existing vpcs that it finds:

```
[brukbook.local:~] brukshut% ./describe_vpcs.rb -r us-west-1

variable "vpcs" {
  type = "map"

  default = {
    bruknet = "vpc-023asdfcbc70c9e" // (10.0.0.0/22)
  }
}
```
If you pass the name of the vpc, or a csv separated list of vpcs, it will generate map variables for public and private subnets for those vpcs:
```
[brukbook.local:~] brukshut% describe_vpcs.rb -r us-west-1 -n bruknet
variable "vpcs" {
  type = "map"

  default = {
    bruknet = "vpc-023asdfcbc70c9e" // (10.0.0.0/22)
  }
}

variable "public_subnets" {
  type = "map"

  default = {
    bruknet-public-1 = "subnet-0222348b9d00bdd56" // bruknet us-west-1a (10.0.0.0/24)
    bruknet-public-2 = "subnet-033234cb1fba656ab" // bruknet us-west-1a (10.0.1.0/24)
  }
}

variable "private_subnets" {
  type = "map"

  default = {
    bruknet-private-1 = "subnet-0asdff7a753bac2c" // bruknet us-west-1a (10.0.2.0/24)
    bruknet-private-2 = "subnet-0asdf2248de5ae93" // bruknet us-west-1a (10.0.3.0/24)
  }
}
```

## make_cert.sh

Generates a 4096 bit rsa key, a certificate signing request and a self signed certificate. Requires a common name.

```
[brukbook.local:~] brukshut% ./make_cert.sh
Usage: ./make_cert.sh -c [commonname]
```

## mk_passwd.py

Generates cryptographically secure random strings (uses Python's `secrets` module). By default it prints one 32-character string containing at least one lowercase letter, uppercase letter, digit and special character. The characters `\/[]{}()` are left out of the default special set because they often need escaping.

```
./mk_passwd.py                          # 32 chars, all classes
./mk_passwd.py -l 64 -S                 # 64 chars, no special characters
./mk_passwd.py -x '$`"'\''' -n 5          # 5 passwords, stripping shell-hostile characters
./mk_passwd.py --special-chars '!@#-_' -A   # custom special set, no look-alike characters
./mk_passwd.py -l 40 --hex              # hex token
./mk_passwd.py -r -l 16                 # readable: e.g. CQgu-Rf5n-RBzm-VJU9
```

`-r/--readable` produces output that is easy to read aloud or type from a screen. It leaves out look-alike characters (`0 O o 1 l I |` and quotes) and special characters, and splits the result into dash-separated groups of 4. Use `-g N` to change the group size (`-g 0` turns grouping off) and `--separator` to change the separator. `--length` counts only the random characters, not the separators. To keep some special characters in readable mode, list them with `--special-chars`.

`-p/--passphrase` generates a passphrase of random words instead, such as `confound-rasping-moneyless-recoup-borrowing-affirm`. The default is 6 words (about 77 bits of entropy). Change the count with `-w N`, the joining character with `--separator`, and add `-C` to capitalize each word or `--with-number` to put one random digit on one word. These help when a password policy requires uppercase letters or digits. Use `--wordlist PATH` to supply your own list, one word per line.

```
./mk_passwd.py -p                       # frozen-pacifism-unequal-hurdle-unending-unflawed
./mk_passwd.py -p -w 5 -C --with-number --separator .   # Unison.Camping.Unleveled.Company3.Posting
```

The default wordlist, `wordlists/eff_large_wordlist.txt`, is the [EFF Large Wordlist](https://www.eff.org/dice) by the Electronic Frontier Foundation, licensed under [CC BY 3.0 US](https://creativecommons.org/licenses/by/3.0/us/). Keep the `wordlists/` directory next to the script.

Run `./mk_passwd.py -h` for all options.
