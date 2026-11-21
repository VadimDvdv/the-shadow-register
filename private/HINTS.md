# Hints

Tier 1: Study which signals can independently cause `grant` to assert.

Tier 2: The diagnostic block may make an assumption about the result of an
authentication attempt. Which observable signal actually proves success?

Tier 3 (strong): Leaving `auth_check` does not always mean success. A soft
reset can terminate `CHECK` without an `auth_fail` pulse.

Do not ship these hints in the public ZIP or README.
