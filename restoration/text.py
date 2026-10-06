"""Display helpers for LoC name strings (LoC stores names lower-case)."""


def name_case(s: str) -> str:
    """"europe's society orchestra" -> "Europe's Society Orchestra" (unlike str.title)."""
    small = {"and", "of", "the"}
    out = []
    for i, w in enumerate(s.split()):
        if (i and w in small) or w.startswith("[i.e."):
            out.append(w)
        elif w.startswith("["):
            out.append("[" + w[1:2].upper() + w[2:])
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)
