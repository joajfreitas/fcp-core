FILE=fcp
FLAGS=--shell-escape -pdf -f -interaction=nonstopmode
make:
	pdflatex $(FLAGS) $(FILE).tex
	pdflatex $(FLAGS) $(FILE).tex

#############################################################
# Maintenance

# compress with ghostscript
gs:
	gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dNOPAUSE -dQUIET -dBATCH -sOutputFile=$(FILE)-compressed.pdf $(FILE).pdf


# leaves pdf
clean:
	@ rm -f $(FILE).log $(FILE).aux $(FILE).toc $(FILE).blg $(FILE).bbl $(FILE).out $(FILE).fls $(FILE).fdb_latexmk $(FILE).glo $(FILE).lof $(FILE).lot $(FILE).nlg $(FILE).nlo $(FILE).nls

# leaves only the source
cleanall:
	@ rm -rf *.log *.aux *.toc *.blg *.bbl *.out *.fls *.fdb_latexmk *.glo *.lof *.lot *.nlg *.nlo *.nls *.pdf *-compressed.pdf _minted*
