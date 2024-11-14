import pandas as pd
import subprocess
import os

# Paths for the files
csv_file = '/Users/matthewmiller/morphhb/verse_morphology - verse_morphology.csv'
tex_file = os.path.expanduser("~/Desktop/genesis_1_verses.tex")
pdf_file = os.path.expanduser("~/Desktop/genesis_1_verses.pdf")

# Load the CSV file
data = pd.read_csv(csv_file, dtype=str)

# Filter Genesis 1 verses only
genesis_1 = data[data['Verse ID'].str.startswith("Gen.1.")]

# Begin LaTeX document structure with a simplified preamble for xelatex
latex_content = r"""
\documentclass{article}
\usepackage{fontspec}
\usepackage{polyglossia}
\usepackage{tcolorbox}
\setdefaultlanguage{english}
\setotherlanguage{hebrew}
\newfontfamily\hebrewfont[Script=Hebrew]{Times New Roman} % Choose a font with Hebrew support

\title{Genesis Chapter 1 Verses}
\date{}

\begin{document}
\maketitle
\section*{Genesis Chapter 1}
\newcommand{\bibleverse}[2]{\textbf{Verse #1:} #2}

\subsection*{Verses}
"""

# Add each verse with each word in individual boxes
for verse_id, verse_data in genesis_1.groupby('Verse ID'):
    verse_label = verse_id.replace('Gen.1.', '1:')
    latex_content += f"\\textbf{{Verse {verse_label}}}\n\n"
    words = verse_data['Word Text'].dropna().tolist()
    for word in words:
        latex_content += f"\\begin{{tcolorbox}}[sharp corners, colframe=black!75, colback=white!90] \\hebrewfont {word} \\end{{tcolorbox}} "
    latex_content += "\n\n"

# Close the document structure
latex_content += r"""
\end{document}
"""

# Save to .tex file
with open(tex_file, 'w') as file:
    file.write(latex_content)

# Compile to PDF with xelatex for better font support
subprocess.run(["xelatex", "-interaction=nonstopmode", "-output-directory", os.path.expanduser("~/Desktop"), tex_file])

print(f"LaTeX and PDF files created on Desktop: {tex_file}, {pdf_file}")