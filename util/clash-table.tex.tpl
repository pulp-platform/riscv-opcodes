\documentclass{article}
\usepackage{array,graphicx}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{pifont}
\usepackage[paperheight=20cm,paperwidth=20cm,margin=0.5cm]{geometry}

\newcommand*\tick{\color{green}{\ding{51}}}
\newcommand*\own{\color{lightgray}{\ding{108}}}

\begin{document}
\thispagestyle{empty}

\begin{table} \centering
    \resizebox{\textwidth}{!}{% use resizebox with textwidth
        \begin{tabular}{${tabs}}
${headers}
            \toprule
${content}
            \bottomrule
        \end{tabular}
    }
\end{table}

\end{document}
