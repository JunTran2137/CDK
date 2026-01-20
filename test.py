import re

pattern = re.compile("^[^&;|\-$()`\n\t]*&(submit|Submit|Login|user_token|password)")

tests = ["username=admin&password=1234&login=login&user_token=abcd"]

for s in tests:
    matches = pattern.findall(s)
    print(f"{s!r} -> {matches}")
