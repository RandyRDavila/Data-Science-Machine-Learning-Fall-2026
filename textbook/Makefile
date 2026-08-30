LATEXMK ?= latexmk
SOURCE := textbook.tex
BUILD_DIR := build
OUTPUT_DIR := ../output/pdf
OUTPUT_PDF := $(OUTPUT_DIR)/data-science-machine-learning-textbook.pdf

.PHONY: all clean

all: $(OUTPUT_PDF)

$(OUTPUT_PDF): $(SOURCE) style/rice-dsm-book.sty $(wildcard frontmatter/*.tex) $(wildcard chapters/*.tex) $(wildcard appendices/*.tex)
	mkdir -p $(BUILD_DIR) $(OUTPUT_DIR)
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=$(BUILD_DIR) $(SOURCE)
	cp $(BUILD_DIR)/textbook.pdf $(OUTPUT_PDF)

clean:
	$(LATEXMK) -C -outdir=$(BUILD_DIR) $(SOURCE)
	rm -f $(OUTPUT_PDF)
