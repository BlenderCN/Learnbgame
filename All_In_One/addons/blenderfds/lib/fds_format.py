"""BlenderFDS, string formatting for FDS"""

def to_comment(msgs) -> "str":
    """Format comments"""
    # Expected output:
    #   ! msg1
    #   ! msg2
    return "".join(("! {}\n".format(msg) for msg in msgs))
