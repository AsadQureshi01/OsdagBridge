# =============================================================================
# OsdagBridge — Report Style System  (SINGLE SOURCE OF TRUTH)
# =============================================================================
# Every formatting decision for the design report lives in this module:
# page geometry, fonts / spacing, colour palette, table style, header / footer
# theme, figure sizes and chart (matplotlib) appearance.
#
# Chapter / section generators MUST NOT hard-code any of these values — they
# import this module (directly, or through ``tables.py`` / ``charts.py`` which
# themselves consume it).  Change a value here and the whole report follows.
#
# Layout of this file
#   1. Palette
#   2. Page geometry & document settings
#   3. Table style
#   4. Column-width presets
#   5. Header / footer / title-page / heading themes
#   6. Figure & chart (matplotlib) style
#   7. LaTeX generators  (preamble, TOC / chapter formats)
# =============================================================================

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# 1. PALETTE   (name -> HTML hex, no '#')
# ─────────────────────────────────────────────────────────────────────────────
COLORS = {
    "osdagGreen":      "91B014",   # brand colour (rules, headings)
    "osdagGreenDark":  "5F7309",   # section headings
    "tableHeader":     "E9F0C8",   # table header-row shading
    "tableNote":       "555555",   # notes / "continued" captions
    "passGreen":       "2E7D32",
    "warnAmber":       "B7791F",
    "failRed":         "C0392B",
}
# Legacy alias: older chapter code writes \textcolor{red}{FAIL}.  Mapping
# `red` onto the palette keeps that code on-theme without touching call sites.
LEGACY_COLOR_ALIASES = {"red": "failRed"}

# ─────────────────────────────────────────────────────────────────────────────
# 2. PAGE GEOMETRY & DOCUMENT SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
FONT_SIZE_PT = 12
PAPER = "a4paper"
PAPER_WIDTH_CM = 21.0
LINE_STRETCH = 1.15

MARGIN_IN = {"left": 1.0, "right": 1.0, "top": 1.0, "bottom": 1.0}
HEADHEIGHT_PT = 15
HEADSEP_PT = 14
# Footer baseline sits FOOTSKIP below the text block.  Large enough for the
# two-line footer (software-default note + institution line) to clear the body.
FOOTSKIP_PT = 34

CM_PER_IN = 2.54
TEXT_WIDTH_CM = PAPER_WIDTH_CM - CM_PER_IN * (MARGIN_IN["left"] + MARGIN_IN["right"])

# ─────────────────────────────────────────────────────────────────────────────
# 3. TABLE STYLE
# ─────────────────────────────────────────────────────────────────────────────
TABLE = {
    "tabcolsep_pt": 6,           # horizontal cell padding
    "compact_tabcolsep_pt": 3.5,
    "arraystretch": 1.12,        # row height multiplier
    "extrarowheight_pt": 0.6,
    "rule_width_pt": 0.5,        # outline thickness
    "row_pad_pt": 6,             # extra vertical padding added at every row end
    "lt_pre_pt": 0,              # space above a longtable
    "lt_post_pt": 6,             # space below a longtable
    "align": "center",           # center | left   (longtable placement)
    "header_shade": "tableHeader",
    "needspace_lines": 6,        # min. baselines kept free before a table starts
    "continued_label": "(continued)",
    "continued_footer": "Continued on next page",
    "show_continued_footer": True,
    "fit_safety_cm": 0.15,
    # longtable builds pages from chunks of this many rows and may always break
    # BETWEEN chunks (default 20), which defeats keep-together rows.  Make the
    # chunk larger than any table in the report.
    "chunk_rows": 500,       # margin kept when auto-fitting column widths
}

# Column layouts for repeated component detail tables. Values account for the
# page text width and leave room for the global cell padding and rule widths.
TABLE_SPECS = {
    "cross_bracing_details": (
        r"|L{2.0cm}|L{2.4cm}|L{3.1cm}|L{3.9cm}|C{1.5cm}|"
    ),
    "end_diaphragm_details": (
        r"|L{2.2cm}|L{2.5cm}|L{3.2cm}|L{4.2cm}|"
    ),
    "vehicle_loads": (
        r"|L{5.4cm}|C{2.0cm}|L{5.0cm}|C{1.4cm}|"
    ),
    "footway_loads": (
        r"|L{5.0cm}|C{3.2cm}|C{1.8cm}|L{3.6cm}|"
    ),
    "quantity_bom": (
        r"|C{1.0cm}|L{4.4cm}|C{1.7cm}|C{3.0cm}|C{3.0cm}|"
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. COLUMN-WIDTH PRESETS  (re-used by several chapters)
#    L/C/R{w} = left / centred / right p-columns  (defined in the preamble)
# ─────────────────────────────────────────────────────────────────────────────
SPEC_PARAM_VALUE = r"|L{5.5cm}|p{10.0cm}|"
SPEC_PARAM_VALUE_NARROW = r"|L{5.5cm}|L{8.5cm}|"
SPEC_TITLE_BLOCK = r"|L{4cm}|L{10cm}|"

# ─────────────────────────────────────────────────────────────────────────────
# 5. HEADER / FOOTER / TITLE PAGE / HEADINGS
# ─────────────────────────────────────────────────────────────────────────────
FOOTER_LEFT = r"Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay"
SOFTWARE_DEFAULT_NOTE = r"* Software default value"
HEAD_RULE_PT = 1.0
FOOT_RULE_PT = 1.0
HEADER_FONT = r"\small"
FOOTER_FONT = r"\footnotesize"

TITLE_PAGE = {
    "top_space": r"1.5cm",
    "logo_left_width": r"0.6\textwidth",
    "logo_right_width": r"0.35\textwidth",
    "logo_right_height": r"2.2cm",
    "after_logos": r"1cm",
    "name_size": r"\Huge",
    "tagline_size": r"\large",
    "doc_title_size": r"\Large",
    "gap_after_tagline": r"1.5cm",
    "gap_after_title": r"1.5cm",
}
TITLE_TEXT = {
    "product": "OsdagBridge",
    "tagline": "Open Source Software for Steel Girder Bridge Design",
    "doc_title": "Design Report",
}

# Chapter / section heading look
CHAPTER_FORMAT = r"\normalfont\sffamily\Large\bfseries\centering"
CHAPTER_RULE_PT = 1.2
SECTION_FORMAT = r"\normalfont\sffamily\large\bfseries\color{osdagGreenDark}"
SUBSECTION_FORMAT = r"\normalfont\sffamily\normalsize\bfseries\color{osdagGreenDark}"
CHAPTER_SPACING_AFTER_TOC = {"before": "0pt", "after": "10pt"}   # body chapters
CHAPTER_SPACING_EXEC_SUMMARY = {"before": "-30pt", "after": "10pt"}
TOC_DEPTH = 2

# ─────────────────────────────────────────────────────────────────────────────
# 6. FIGURES & CHARTS
# ─────────────────────────────────────────────────────────────────────────────
FIGURE = {
    "default_width": r"0.85\textwidth",
    "chart_width": r"0.90\textwidth",
    "caption_font": r"\small",
    "placement": "H",
}


def figure_block(path: str, caption: str, width: str | None = None) -> str:
    """Render a consistently sized, centered report figure."""
    width = width or FIGURE["chart_width"]
    return (
        r"\begin{figure}[" + FIGURE["placement"] + r"]\centering"
        + r"\includegraphics[width=" + width + r"]{" + path + "}"
        + r"\caption*{" + FIGURE["caption_font"] + " " + caption + r"}"
        + r"\end{figure}"
    )

CHART = {
    "dpi": 200,
    "figsize": (7.6, 4.1),
    "font_size": 9,
    "title_size": 11,
    "grid_alpha": 0.25,
    "bar_width": 0.62,
    "limit_value": 1.0,                 # UR = 1.0
    "limit_color": "#C0392B",
    "limit_style": "--",
    "limit_width": 1.5,
    "limit_label": "UR = 1.0 (limit)",
    "fail_edge_color": "#C0392B",
    "fail_hatch": "//",
    "value_fmt": "{:.2f}",
    "axis_color": "#444444",
    # one colour per primary structural element
    "element_colors": {
        "Steel Plate Girders": "#5B7DB1",
        "Concrete Deck Slab":  "#8C8C8C",
        "Cross Bracing":       "#91B014",
        "End Diaphragms":      "#D9822B",
    },
    "quantity_colors": {
        "girders":   "#5B7DB1",
        "bracing":   "#91B014",
        "diaphragm": "#D9822B",
        "concrete":  "#8C8C8C",
        "rebar":     "#B5483A",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 7. LATEX GENERATORS
# ─────────────────────────────────────────────────────────────────────────────
_PACKAGES = [
    # (name, options)  — order matters for a few of them (caption before subcaption)
    ("graphicx", ""), ("amsmath", ""), ("amssymb", ""), ("booktabs", ""),
    ("array", ""), ("tabularx", ""), ("float", ""), ("fancyhdr", ""),
    ("hyperref", "hidelinks"), ("xcolor", ""), ("setspace", ""),
    ("enumitem", ""), ("caption", ""), ("subcaption", ""), ("multirow", ""),
    ("colortbl", ""), ("longtable", ""), ("titlesec", ""), ("titletoc", ""),
    ("lastpage", ""), ("makecell", ""), ("etoolbox", ""), ("needspace", ""),
]


def geometry_options() -> str:
    m = MARGIN_IN
    return ("{paper},left={l}in,right={r}in,top={t}in,bottom={b}in,"
            "headheight={hh}pt,headsep={hs}pt,footskip={fs}pt").format(
        paper=PAPER, l=m["left"], r=m["right"], t=m["top"], b=m["bottom"],
        hh=HEADHEIGHT_PT, hs=HEADSEP_PT, fs=FOOTSKIP_PT)


def color_definitions() -> str:
    lines = [r"\definecolor{%s}{HTML}{%s}" % (k, v) for k, v in COLORS.items()]
    lines += [r"\colorlet{%s}{%s}" % (alias, target)
              for alias, target in LEGACY_COLOR_ALIASES.items()]
    return "\n".join(lines)


def table_layout() -> str:
    t = TABLE
    ltside = r"\fill" if t["align"] == "center" else "0pt"
    return "\n".join([
        r"\LTchunksize=%d" % t["chunk_rows"],
        r"\setlength{\LTleft}{%s}" % ltside,
        r"\setlength{\LTright}{\fill}",
        r"\setlength{\tabcolsep}{%spt}" % t["tabcolsep_pt"],
        r"\renewcommand{\arraystretch}{%s}" % t["arraystretch"],
        r"\setlength{\LTpre}{%spt}" % t["lt_pre_pt"],
        r"\setlength{\LTpost}{%spt}" % t["lt_post_pt"],
        r"\setlength{\arrayrulewidth}{%spt}" % t["rule_width_pt"],
        r"\setlength{\extrarowheight}{%spt}" % t["extrarowheight_pt"],
        # Keep a table's caption + first rows together: if fewer than N lines
        # remain on the page, start the table on the next one.
        r"\BeforeBeginEnvironment{table}{\needspace{%d\baselineskip}}" % t["needspace_lines"],
        r"\BeforeBeginEnvironment{longtable}{\needspace{%d\baselineskip}}" % t["needspace_lines"],
        # LaTeX's \cline is a row of its own with a break point after it, which
        # lets a multirow block split across pages.  Same definition, plus \nobreak.
        r"\makeatletter",
        r"\def\@cline#1-#2\@nil{\omit\@multicnt#1\advance\@multispan\m@ne",
        r"  \ifnum\@multicnt=\@ne\@firstofone{&\omit}\fi",
        r"  \@multicnt#2\advance\@multicnt-#1\advance\@multispan\@ne",
        r"  \leaders\hrule\@height\arrayrulewidth\hfill\cr",
        r"  \noalign{\nobreak\vskip-\arrayrulewidth\nobreak}}",
        r"\makeatother",
    ])


def _page_style(name: str, head_left: str, head_right: str, with_head: bool) -> str:
    """One fancyhdr page style.  The footer is two lines at most: an optional
    "software default" note above the institution line.  No negative vertical
    skips are used, so the footer can never creep up into the text block."""
    out = [r"\fancypagestyle{%s}{" % name, r"  \fancyhf{}"]
    if with_head:
        out += [
            r"  \fancyhead[L]{%s %s}" % (HEADER_FONT, head_left),
            r"  \fancyhead[R]{%s %s}" % (HEADER_FONT, head_right),
            r"  \renewcommand{\headrulewidth}{%spt}" % HEAD_RULE_PT,
            r"  \renewcommand{\headrule}{\hbox to\headwidth{\color{osdagGreen}"
            r"\leaders\hrule height \headrulewidth\hfill}}",
        ]
    else:
        out.append(r"  \renewcommand{\headrulewidth}{0pt}")
    out += [
        r"  \fancyfoot[L]{\parbox[b]{0.72\headwidth}{\raggedright"
        r"\ifbool{hasSDonPage}{%s\itshape %s\par}{}%s %s}}"
        % (FOOTER_FONT, SOFTWARE_DEFAULT_NOTE, FOOTER_FONT, FOOTER_LEFT),
        r"  \fancyfoot[R]{%s Page \thepage\ of \pageref{LastPage}}" % FOOTER_FONT,
        r"  \renewcommand{\footrulewidth}{%spt}" % FOOT_RULE_PT,
        r"  \renewcommand{\footrule}{\hbox to\headwidth{\color{osdagGreen}"
        r"\leaders\hrule height \footrulewidth\hfill}}",
        r"}",
    ]
    return "\n".join(out)


def heading_formats() -> str:
    return "\n".join([
        r"\titleformat{\chapter}[block]{%s}{\thechapter}{1em}{}"
        r"[{\color{osdagGreen}\titlerule[%spt]}]" % (CHAPTER_FORMAT, CHAPTER_RULE_PT),
        r"\titleformat{\section}{%s}{\thesection}{0.8em}{}" % SECTION_FORMAT,
        r"\titleformat{\subsection}{%s}{\thesubsection}{0.8em}{}" % SUBSECTION_FORMAT,
    ])


def chapter_spacing(kind: str = "body") -> str:
    sp = CHAPTER_SPACING_EXEC_SUMMARY if kind == "exec" else CHAPTER_SPACING_AFTER_TOC
    return r"\titlespacing*{\chapter}{0pt}{%s}{%s}" % (sp["before"], sp["after"])


def restore_chapter_format() -> str:
    """LaTeX snippet used after the (unnumbered) executive summary."""
    return heading_formats().split("\n")[0] + "\n" + chapter_spacing("exec")


def build_preamble(project_name: str, job_number: str, report_date: str,
                   report_version: str = "Rev 0") -> str:
    """Return everything from \\documentclass to \\begin{document}.
    All four arguments must already be LaTeX-escaped by the caller."""
    head_left = r"%s $|$ %s" % (project_name, job_number)
    head_right = r"%s $|$ %s" % (report_date, report_version)
    pk = "\n".join(
        (r"\usepackage[%s]{%s}" % (o, n)) if o else (r"\usepackage{%s}" % n)
        for n, o in _PACKAGES)
    t = TITLE_TEXT
    return "\n".join([
        r"\documentclass[%dpt,%s]{report}" % (FONT_SIZE_PT, PAPER),
        "",
        r"\usepackage[%s]{geometry}" % geometry_options(),
        pk,
        r"\captionsetup{labelfont=bf,justification=raggedright,"
        r"singlelinecheck=false,format=plain,skip=4pt}",
        r"\numberwithin{table}{chapter}",
        r"\numberwithin{figure}{chapter}",
        "",
        "% --- palette ---",
        color_definitions(),
        "",
        "% --- table layout ---",
        table_layout(),
        "",
        "% --- text flow ---",
        r"\widowpenalty=10000",
        r"\clubpenalty=10000",
        r"\raggedbottom",
        "",
        "% --- header / footer themes ---",
        r"\newbool{hasSDonPage}",
        r"\boolfalse{hasSDonPage}",
        r"\newcommand{\markSD}{\global\booltrue{hasSDonPage}}",
        r"\newcommand{\sdstar}{\textsuperscript{*}\markSD{}}",
        r"\AddToHook{shipout/before}{\global\boolfalse{hasSDonPage}}",
        _page_style("main", head_left, head_right, True),
        _page_style("plain", head_left, head_right, True),
        _page_style("firstpage", "", "", False),
        r"\pagestyle{main}",
        r"\setstretch{%s}" % LINE_STRETCH,
        "",
        toc_style(),
        "",
        "% --- custom commands & column types ---",
        r"\newcommand{\placeholder}[1]{\textit{\textless #1\textgreater}}",
        r"\newcommand{\todo}[1]{\colorbox{yellow}{TODO: #1}}",
        r"\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}",
        r"\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}",
        r"\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}",
        "",
        r"\title{\Large\textbf{%s} \\ \normalsize %s \\ \vspace{2cm} "
        r"\large %s}" % (t["product"], t["tagline"], t["doc_title"]),
        r"\author{}",
        r"\date{}",
        "",
        r"\begin{document}",
        "",
    ])


def toc_style() -> str:
    """Heading + table-of-contents styling (emitted in the preamble so it applies
    whether or not a TOC is included)."""
    return "\n".join([
        "% --- headings & TOC styling ---",
        heading_formats(),
        chapter_spacing("body"),
        r"\setcounter{tocdepth}{%d}" % TOC_DEPTH,
        r"\titlecontents{chapter}[1.5em]{\normalfont\vspace{2pt}}"
        r"{\contentslabel{1.5em}}{\hspace*{-1.5em}}{\hfill\contentspage}",
        r"\titlecontents{section}[3.8em]{\normalfont}"
        r"{\contentslabel{2.3em}}{\hspace*{-2.3em}}{\hfill\contentspage}",
        r"\titlecontents{subsection}[7.0em]{\normalfont}"
        r"{\contentslabel{3.2em}}{\hspace*{-3.2em}}{\hfill\contentspage}",
    ])


def toc_format() -> str:
    """Table-of-contents page (body of the document)."""
    return "\n".join([
        r"\newpage",
        r"\renewcommand{\contentsname}{\centering\Large\bfseries Table of Contents}",
        r"\tableofcontents",
        "",
    ])
