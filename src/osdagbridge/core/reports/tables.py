# =============================================================================
# OsdagBridge — Report table helpers
# =============================================================================
# All tables in the design report are built through this module so that they
#   1. repeat their column header on every page they span
#      (\endfirsthead / \endhead + "continued" caption + "continued" footer),
#   2. fit inside the text block (fixed-cm column widths are scaled down when a
#      specification would overflow the page margins),
#   3. never split a multirow block across a page break
#      (rows of one block are glued with \\* so a label like "G4" cannot be
#      left hanging below its rows and bleed into the footer), and
#   4. take their padding / shading / rules from ``styles.TABLE``.
#
# No formatting constants live here — they all come from ``styles``.
# =============================================================================

from __future__ import annotations

import re
from typing import Iterable, Optional, Sequence

from osdagbridge.core.reports import styles as S

_PT_PER_CM = 72.27 / 2.54

# ─────────────────────────────────────────────────────────────────────────────
# Column-spec parsing / auto-fit
# ─────────────────────────────────────────────────────────────────────────────

def _skip_group(s: str, i: int) -> int:
    """s[i] == '{' → index just after the matching '}'."""
    depth = 0
    while i < len(s):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return i


def parse_colspec(spec: str):
    """Return (columns, n_rules).  ``columns`` is a list of dicts
    {kind, w (cm or None), span (start, end) of the width text in ``spec``}."""
    cols, n_rules, i = [], 0, 0
    while i < len(spec):
        ch = spec[i]
        if ch == "|":
            n_rules += 1
            i += 1
        elif ch in "><@!":
            i = _skip_group(spec, i + 1) if i + 1 < len(spec) and spec[i + 1] == "{" else i + 1
        elif ch in "pmbLCR" and i + 1 < len(spec) and spec[i + 1] == "{":
            end = _skip_group(spec, i + 1)
            inner = spec[i + 2:end - 1]
            m = re.fullmatch(r"\s*([0-9]*\.?[0-9]+)\s*cm\s*", inner)
            cols.append({"kind": ch, "w": float(m.group(1)) if m else None,
                         "span": (i + 2, end - 1)})
            i = end
        elif ch in "lcrX":
            cols.append({"kind": ch, "w": None, "span": None})
            i += 1
        else:
            i += 1
    return cols, n_rules


def count_columns(spec: str) -> int:
    return len(parse_colspec(spec)[0])


def fit_colspec(spec: str, tabcolsep_pt: Optional[float] = None) -> str:
    """Scale fixed-cm column widths down so the whole table fits the text block.
    Specs that already fit are returned unchanged."""
    tc = S.TABLE["tabcolsep_pt"] if tabcolsep_pt is None else tabcolsep_pt
    cols, n_rules = parse_colspec(spec)
    widths = [c["w"] for c in cols if c["w"] is not None]
    if not widths:
        return spec
    pad_cm = len(cols) * 2.0 * tc / _PT_PER_CM
    rule_cm = n_rules * S.TABLE["rule_width_pt"] / _PT_PER_CM
    avail = S.TEXT_WIDTH_CM - pad_cm - rule_cm - S.TABLE["fit_safety_cm"]
    total = sum(widths)
    if total <= avail or avail <= 0:
        return spec
    k = avail / total
    out, last = [], 0
    for c in cols:
        if c["w"] is None:
            continue
        a, b = c["span"]
        out.append(spec[last:a])
        out.append("%.2fcm" % (c["w"] * k))
        last = b
    out.append(spec[last:])
    return "".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# Row helpers
# ─────────────────────────────────────────────────────────────────────────────

def row_end(keep_with_next: bool = False) -> str:
    """Row terminator carrying the themed padding.  ``keep_with_next`` forbids
    a page break after the row (use inside multirow blocks)."""
    return r"\\%s[%spt]" % ("*" if keep_with_next else "", S.TABLE["row_pad_pt"])


def table_row(cells: Iterable[str], rule: str = r"\hline", keep_with_next: bool = False) -> str:
    return " & ".join(cells) + " " + row_end(keep_with_next) + ("\n" + rule if rule else "")


def _bold(cell: str) -> str:
    cell = cell.strip()
    return r"\textbf{%s}" % cell if cell else ""


def _strip_bold(text: str) -> str:
    m = re.fullmatch(r"\s*\\textbf\{(.*)\}\s*", text, flags=re.S)
    return m.group(1) if m else text


def _header_block(header: Optional[Sequence[str]], header_raw: Optional[str]) -> str:
    if header_raw is not None:
        return header_raw.strip("\n")
    if header:
        return (r"\rowcolor{%s}" % S.TABLE["header_shade"]
                + " & ".join(_bold(c) for c in header) + " " + row_end()
                + "\n\\hline")
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# Longtable with repeating header
# ─────────────────────────────────────────────────────────────────────────────

def lt_head(spec: str, caption: str, header: Optional[Sequence[str]] = None, *,
            header_raw: Optional[str] = None, label: Optional[str] = None,
            tabcolsep_pt: Optional[float] = None, fit: bool = True) -> str:
    """Everything from \\begin{longtable} up to and including \\endlastfoot.
    The caller then appends the body rows and ``\\end{longtable}``.

    header      list of column titles (auto-bolded, header-row shaded) or
    header_raw  a verbatim multi-row header (must carry its own \\hline's).
    """
    if fit:
        spec = fit_colspec(spec, tabcolsep_pt)
    n = count_columns(spec)
    hdr = _header_block(header, header_raw)
    cap = r"\caption{\textbf{%s}}" % _strip_bold(caption)
    if label:
        cap += r"\label{%s}" % label
    cont = (r"\multicolumn{%d}{l}{\footnotesize\itshape\textcolor{tableNote}"
            r"{Table \thetable\ %s}}\\" % (n, S.TABLE["continued_label"]))
    lines = [
        r"\begin{longtable}{%s}" % spec,
        cap + r"\\",
        r"\hline",
        hdr,
        r"\endfirsthead",
        cont,
        r"\hline",
        hdr,
        r"\endhead",
    ]
    if S.TABLE["show_continued_footer"]:
        lines += [r"\multicolumn{%d}{r}{\footnotesize\itshape\textcolor{tableNote}"
                  r"{%s}}\\" % (n, S.TABLE["continued_footer"]),
                  r"\endfoot"]
    lines.append(r"\endlastfoot")
    return "\n".join(x for x in lines if x != "")


def lt(spec: str, caption: str, header: Optional[Sequence[str]], body: str, **kw) -> str:
    """Complete longtable: head + body + \\end{longtable}."""
    return lt_head(spec, caption, header, **kw) + "\n" + body.strip("\n") + "\n\\end{longtable}\n"


# ─────────────────────────────────────────────────────────────────────────────
# Whole-document normalisation  (applied once, in report_generator)
# ─────────────────────────────────────────────────────────────────────────────

# A row end directly followed by \cline is *inside* a multirow block (the last
# row of a block is followed by \hline).  Glue those rows together.
_RE_KEEP = re.compile(r"\\\\(?!\*)(\[[^\]]*\])?(\s*)\\cline")
# Legacy hard-coded row paddings used by the chapter code.
_RE_PAD = re.compile(r"\\\\(\*?)\[(?:6|8)pt\]")


def keep_groups_together(tex: str) -> str:
    # \\* forbids a page break after the row.  (The preamble also patches \cline
    # so that no break can occur after the rule row — see styles.table_layout.)
    return _RE_KEEP.sub(lambda m: r"\\*" + (m.group(1) or "") + m.group(2) + r"\cline", tex)


def normalise_row_padding(tex: str) -> str:
    pad = S.TABLE["row_pad_pt"]
    return _RE_PAD.sub(lambda m: r"\\%s[%spt]" % (m.group(1), pad), tex)


def finalize_tex(tex: str) -> str:
    """Apply global table rules and add repeating heads to legacy longtables."""
    tex = repeat_legacy_headers(tex)
    return normalise_row_padding(keep_groups_together(tex))


def _balanced_brace_end(text: str, start: int) -> int:
    """Return the character after the closing brace matching ``start``."""
    if start >= len(text) or text[start] != "{":
        return start
    depth = 0
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{" and not escaped:
            depth += 1
        elif ch == "}" and not escaped:
            depth -= 1
            if depth == 0:
                return i + 1
        if ch == "\\" and not escaped:
            escaped = True
        else:
            escaped = False
    return start


def repeat_legacy_headers(tex: str) -> str:
    """Give existing chapter longtables a repeated copy of their first header.

    Tables authored with :func:`lt_head` already carry explicit repeat blocks.
    The project also has many hand-written tables; for those, copy the first
    row between the caption rule and the next rule into longtable's head blocks.
    Tables without a recognizable header are left intact.
    """
    table_re = re.compile(r"\\begin\{longtable\}(?:\[[^\]]*\])?")
    row_re = re.compile(r"\\hline\s*(?P<header>.*?)\\\\(?:\[[^\]]*\])?\s*\\hline", re.S)

    def convert(block):
        begin = table_re.match(block)
        if begin is None:
            return block
        spec_start = begin.end()
        while spec_start < len(block) and block[spec_start].isspace():
            spec_start += 1
        spec_end = _balanced_brace_end(block, spec_start)
        if spec_end == spec_start:
            return block

        original_spec = block[spec_start + 1:spec_end - 1]
        spec = fit_colspec(original_spec)
        if spec != original_spec:
            block = block[:spec_start + 1] + spec + block[spec_end - 1:]
        n = count_columns(spec)
        if r"\endfirsthead" in block:
            # Explicit longtables authored by chapter modules already carry
            # both heads; apply the central header treatment without adding a
            # second repeated-head block.
            # Earlier report builds could calculate this span from the whole
            # table body (for example, 51 columns in a two-column table).
            block = re.sub(
                r"(\\multicolumn\{)\d+(\}\{l\}\{\\footnotesize\\itshape"
                r"\\textcolor\{tableNote\}\{Table \\thetable)",
                lambda m: m.group(1) + str(n) + m.group(2), block)
            insertions = []
            for header_match in row_re.finditer(block):
                if (r"\textbf" in header_match.group("header")
                        and r"\rowcolor" not in block[max(0, header_match.start() - 35):header_match.start()]):
                    insertions.append(header_match.start("header"))
            for pos in reversed(insertions):
                block = block[:pos] + r"\rowcolor{%s}" % S.TABLE["header_shade"] + "\n" + block[pos:]
            return block

        # Legacy longtables often put \hline immediately after \caption.
        # Unlike the helper-generated tables, that leaves the caption as an
        # unfinished longtable row and can make the first and continued heads
        # appear together when the table starts near a page boundary.  Close
        # the caption row before building the repeated heads.
        caption_at = block.find(r"\caption")
        if caption_at >= 0:
            caption_brace = block.find("{", caption_at)
            caption_end = _balanced_brace_end(block, caption_brace)
            if caption_end > caption_brace:
                after_caption = caption_end
                while after_caption < len(block) and block[after_caption].isspace():
                    after_caption += 1
                if block.startswith(r"\label", after_caption):
                    label_brace = block.find("{", after_caption)
                    label_end = _balanced_brace_end(block, label_brace)
                    if label_end > label_brace:
                        after_caption = label_end
                        while after_caption < len(block) and block[after_caption].isspace():
                            after_caption += 1
                if block.startswith(r"\hline", after_caption):
                    block = block[:after_caption] + r"\\" + "\n" + block[after_caption:]

        header_match = row_re.search(block)
        if not header_match or r"\textbf" not in header_match.group("header"):
            return block
        original_header = header_match.group("header")
        header = r"\rowcolor{%s}" % S.TABLE["header_shade"] + "\n" + original_header.strip()
        block = (block[:header_match.start("header")] + header
                 + block[header_match.end("header"):])
        header_end = header_match.end() + len(header) - len(original_header)
        continued = (r"\multicolumn{%d}{l}{\footnotesize\itshape\textcolor{tableNote}"
                     r"{Table \thetable %s}}\\" % (n, S.TABLE["continued_label"]))
        repeat = ("\\endfirsthead\n" + continued + "\n\\hline\n" + header
                  + "\\\\[" + str(S.TABLE["row_pad_pt"]) + "pt]\n\\hline\n\\endhead\n")
        return block[:header_end] + "\n" + repeat + block[header_end:]

    chunks = []
    cursor = 0
    for match in table_re.finditer(tex):
        end = tex.find(r"\end{longtable}", match.end())
        if end < 0:
            break
        end += len(r"\end{longtable}")
        chunks.append(tex[cursor:match.start()])
        chunks.append(convert(tex[match.start():end]))
        cursor = end
    chunks.append(tex[cursor:])
    return "".join(chunks)
