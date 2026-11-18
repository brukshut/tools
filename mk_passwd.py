#!/usr/bin/env python3

##
## generate cryptographically secure random strings / passwords
##
import argparse
import math
import os
import secrets
import string
import sys

## characters historically stripped from the special set because they
## tend to cause quoting/escaping trouble in shells, json, yaml, etc.
DEFAULT_SPECIAL_EXCLUDE = '\\/[]{}()'

## characters that are easily confused with one another when read by a human
AMBIGUOUS = '0Oo1lI|`\'"'

## diceware wordlist shipped next to this script (resolves symlinks)
DEFAULT_WORDLIST = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'wordlists', 'eff_large_wordlist.txt')

## functions
def build_classes(args):
  """Return a list of character pools, one per enabled character class."""
  classes = []
  if not args.no_lower:
    classes.append(string.ascii_lowercase)
  if not args.no_upper:
    classes.append(string.ascii_uppercase)
  if not args.no_digits:
    classes.append(string.digits)
  if not args.no_special:
    if args.special_chars is not None:
      special = args.special_chars
    else:
      special = ''.join(c for c in string.punctuation if c not in DEFAULT_SPECIAL_EXCLUDE)
    classes.append(special)

  ## strip excluded characters from every class
  exclude = set(args.exclude or '')
  if args.no_ambiguous:
    exclude.update(AMBIGUOUS)
  classes = [''.join(sorted(set(c) - exclude)) for c in classes]

  ## a class emptied by exclusions can't be required, so drop it
  return [c for c in classes if c]


def random_string(length, classes, require_each=True):
  """Generate a random string of the given length using a CSPRNG.

  When require_each is true, the result contains at least one character
  from every class in `classes`.
  """
  alphabet = ''.join(sorted(set(''.join(classes))))
  chars = []
  if require_each:
    chars = [secrets.choice(c) for c in classes]
  chars += [secrets.choice(alphabet) for _ in range(length - len(chars))]
  ## shuffle so the required characters aren't always at the front
  secrets.SystemRandom().shuffle(chars)
  return ''.join(chars)


def entropy_bits(length, alphabet_size):
  return length * math.log2(alphabet_size) if alphabet_size > 1 else 0.0


def positive_int(value):
  try:
    n = int(value)
  except ValueError:
    raise argparse.ArgumentTypeError(f"'{value}' is not an integer")
  if n < 1:
    raise argparse.ArgumentTypeError(f"must be >= 1, got {n}")
  return n


def non_negative_int(value):
  try:
    n = int(value)
  except ValueError:
    raise argparse.ArgumentTypeError(f"'{value}' is not an integer")
  if n < 0:
    raise argparse.ArgumentTypeError(f"must be >= 0, got {n}")
  return n


def group(s, size, separator):
  """Split s into chunks of `size` joined by `separator` (size 0 = no grouping)."""
  if size <= 0:
    return s
  return separator.join(s[i:i + size] for i in range(0, len(s), size))


def load_wordlist(path, separator=''):
  """Load a wordlist: one word per line, optionally prefixed by diceware numbers.

  Words containing the separator are dropped so the passphrase can always be
  split back into its words.
  """
  words = set()
  with open(path, encoding='utf-8') as f:
    for line in f:
      fields = line.split()
      if not fields:
        continue
      word = fields[-1].lower()
      if separator and separator in word:
        continue
      words.add(word)
  return sorted(words)


def make_passphrase(words, count, separator='-', capitalize=False, with_number=False):
  """Join `count` words chosen with a CSPRNG."""
  chosen = [secrets.choice(words) for _ in range(count)]
  if capitalize:
    chosen = [w.capitalize() for w in chosen]
  if with_number:
    chosen[secrets.randbelow(count)] += str(secrets.randbelow(10))
  return separator.join(chosen)


def passphrase_main(args):
  path = args.wordlist or DEFAULT_WORDLIST
  try:
    words = load_wordlist(path, args.separator)
  except OSError as e:
    sys.exit(f"error: cannot read wordlist {path}: {e.strerror}")
  if len(words) < 2:
    sys.exit(f"error: wordlist {path} has fewer than 2 usable words")

  bits = args.words * math.log2(len(words))
  if args.with_number:
    bits += math.log2(10) + math.log2(args.words)

  if args.verbose:
    print(f"wordlist: {len(words)} words, entropy: ~{bits:.0f} bits per passphrase", file=sys.stderr)
  if bits < 64:
    print(f"warning: only ~{bits:.0f} bits of entropy; consider more words (-w) or a larger wordlist", file=sys.stderr)

  for _ in range(args.count):
    print(make_passphrase(words, args.words, args.separator, args.capitalize, args.with_number))


def argue():
  parser = argparse.ArgumentParser(
    description="Generate cryptographically secure random strings / passwords.",
    epilog=(
      "examples:\n"
      "  %(prog)s                       32 chars, all classes\n"
      "  %(prog)s -l 64 -S              64 chars, no special characters\n"
      "  %(prog)s -x '$`\"\\'' -n 5      5 passwords without shell-hostile chars\n"
      "  %(prog)s --special-chars '!@#%%^*-_=+' -A\n"
      "  %(prog)s -l 40 --hex           40 hex characters (e.g. for tokens)\n"
      "  %(prog)s -r -l 16              e.g. Xk7m-Pq4t-Wz9h-Ab3c\n"
      "  %(prog)s -p                    e.g. ember-unsaid-wobbly-tulip-rascal-gravy\n"
      "  %(prog)s -p -w 5 -C --with-number --separator .\n"
      "                                   e.g. Ember.Unsaid4.Wobbly.Tulip.Rascal"
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )
  parser.add_argument("-l", "--length", type=positive_int, default=32,
                      help="length of each string (default: 32)")
  parser.add_argument("-n", "--count", type=positive_int, default=1,
                      help="number of strings to generate (default: 1)")

  classes = parser.add_argument_group("character classes")
  classes.add_argument("-S", "--no-special", action="store_true",
                       help="do not use special characters (alphanumeric only)")
  classes.add_argument("-U", "--no-upper", action="store_true",
                       help="do not use uppercase letters")
  classes.add_argument("-L", "--no-lower", action="store_true",
                       help="do not use lowercase letters")
  classes.add_argument("-D", "--no-digits", action="store_true",
                       help="do not use digits")
  classes.add_argument("--special-chars", metavar="CHARS",
                       help="use exactly these special characters instead of the default set "
                            f"(default: punctuation minus {DEFAULT_SPECIAL_EXCLUDE})")
  classes.add_argument("--hex", action="store_true",
                       help="lowercase hex output only (0-9a-f); ignores other class options")

  strip = parser.add_argument_group("excluding characters")
  strip.add_argument("-x", "--exclude", metavar="CHARS", default="",
                     help="strip these characters from the output alphabet")
  strip.add_argument("-A", "--no-ambiguous", action="store_true",
                     help=f"strip easily-confused characters ({AMBIGUOUS})")

  readable = parser.add_argument_group("readability")
  readable.add_argument("-r", "--readable", action="store_true",
                        help="human-friendly output: implies --no-ambiguous, drops special "
                             "characters (unless --special-chars is given), and groups into "
                             "chunks of 4 separated by '-'")
  readable.add_argument("-g", "--group", type=non_negative_int, metavar="N",
                        help="insert a separator every N characters (0 = off; default: 4 with "
                             "--readable, otherwise off). Separators don't count toward --length")
  readable.add_argument("--separator", default="-", metavar="CHAR",
                        help="separator used by --group and between passphrase words (default: -)")

  phrase = parser.add_argument_group("passphrase mode (ignores character and length options)")
  phrase.add_argument("-p", "--passphrase", action="store_true",
                      help="generate a passphrase of random words instead of characters")
  phrase.add_argument("-w", "--words", type=positive_int, default=6, metavar="N",
                      help="number of words (default: 6, ~77 bits with the default wordlist)")
  phrase.add_argument("--wordlist", metavar="PATH",
                      help="one word per line, diceware numbers optional "
                           "(default: EFF large wordlist shipped in wordlists/)")
  phrase.add_argument("-C", "--capitalize", action="store_true",
                      help="capitalize each word")
  phrase.add_argument("--with-number", action="store_true",
                      help="append a random digit to one random word")

  parser.add_argument("--no-require-each", action="store_true",
                      help="do not guarantee at least one character from each enabled class")
  parser.add_argument("-v", "--verbose", action="store_true",
                      help="print alphabet size and estimated entropy to stderr")
  return parser.parse_args()


def main():
  args = argue()

  if args.passphrase:
    passphrase_main(args)
    return

  if args.readable:
    args.no_ambiguous = True
    if args.special_chars is None:
      args.no_special = True
    if args.group is None:
      args.group = 4
  group_size = args.group or 0

  ## keep the separator out of the alphabet so the chunks stay unambiguous
  if group_size and args.separator:
    args.exclude = (args.exclude or '') + args.separator

  if args.hex:
    exclude = set(args.exclude)
    if args.no_ambiguous:
      exclude.update(AMBIGUOUS)
    classes = [''.join(c for c in string.digits + 'abcdef' if c not in exclude)]
    classes = [c for c in classes if c]
  else:
    classes = build_classes(args)

  if not classes:
    sys.exit("error: no characters left to choose from; relax your class/exclude options")

  require_each = not args.no_require_each
  if require_each and args.length < len(classes):
    sys.exit(f"error: length {args.length} is too short to include one character from each "
             f"of the {len(classes)} enabled classes (use --no-require-each or a longer length)")

  alphabet_size = len(set(''.join(classes)))
  bits = entropy_bits(args.length, alphabet_size)

  if args.verbose:
    print(f"alphabet: {alphabet_size} chars, entropy: ~{bits:.0f} bits per string", file=sys.stderr)
  if bits < 64:
    print(f"warning: only ~{bits:.0f} bits of entropy; consider a longer length or larger alphabet",
          file=sys.stderr)

  for _ in range(args.count):
    print(group(random_string(args.length, classes, require_each), group_size, args.separator))

## end functions

## main
if __name__ == '__main__':
  main()
## end main
