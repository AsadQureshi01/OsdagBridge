from osdagbridge.core.reports import styles as S


def ch7_quantities(input_dict, chart_paths=None):
    chart_paths = chart_paths or {}
    figures = []
    for key, caption in (("steel_tonnage", "Structural steel quantities by component"),
                         ("concrete_rebar", "Deck concrete and reinforcement quantities")):
        path = chart_paths.get(key)
        if path:
            figures.append(S.figure_block(path, caption))
    figures_tex = "\n".join(figures)
    return r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

\noindent\textbf{Table 7.1  Bill of Materials (Steel, Concrete, and Reinforcement Quantities)}

\begingroup
\setlength{\tabcolsep}{""" + str(S.TABLE["compact_tabcolsep_pt"]) + r"""pt}
\begin{longtable}{""" + S.TABLE_SPECS["quantity_bom"] + r"""}
\rowcolor{tableHeader}
\hline
\textbf{S.N.} & \textbf{Item Description} & \textbf{Quantity} & \textbf{Total Volume (m\textsuperscript{3})} & \textbf{Total Weight (MT)} \\
\hline
1 & Structural Steel (IS 2062) for Girders & """ + str(input_dict.get("steel_girders_qty", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_total", "N.A.")) + r""" \\
\hline
2(a) & Cross Bracing - Top Chord & """ + str(input_dict.get("bracing_top_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_total", "N.A.")) + r""" \\
\hline
2(b) & Cross Bracing - Bottom Chord & """ + str(input_dict.get("bracing_bot_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_total", "N.A.")) + r""" \\
\hline
2(c) & Cross Bracing - Diagonal Members & """ + str(input_dict.get("bracing_diag_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_total", "N.A.")) + r""" \\
\hline
2(d) & End Diaphragms (Steel) & """ + str(input_dict.get("steel_end_diaphragm_qty", "N.A.")) + r""" & """ + str(input_dict.get("steel_end_diaphragm_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("steel_end_diaphragm_wt_total", "N.A.")) + r""" \\
\hline
3 & Concrete (M40) for Deck Slab & """ + str(input_dict.get("concrete_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_total", "N.A.")) + r""" \\
\hline
4 & Reinforcement Steel (Fe 500) & """ + str(input_dict.get("rebar_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_total", "N.A.")) + r""" \\
\hline
5 & Shear Stud Connectors & """ + str(input_dict.get("shear_studs_qty", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_total", "N.A.")) + r""" \\
\hline
6 & Crash Barrier & """ + str(input_dict.get("crash_barrier_qty", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_total", "N.A.")) + r""" \\
\hline
\end{longtable}
\endgroup
\noindent\textit{Note: Quantity is the item count; volume and weight columns show aggregate totals for each line item.}
""" + figures_tex


