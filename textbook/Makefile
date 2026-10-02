LATEXMK ?= latexmk
SOURCE := textbook.tex
BUILD_DIR := build
OUTPUT_DIR := ../output/pdf
OUTPUT_PDF := $(OUTPUT_DIR)/data-science-machine-learning-textbook.pdf
FIGURE_SCRIPT := figures/generate_part_ii_figures.py
FIGURES := figures/generated/learning-landscape.pdf \
	figures/generated/supervised-evidence.pdf \
	figures/generated/regression-geometry.pdf \
	figures/generated/gradient-methods.pdf \
	figures/generated/logistic-single-neuron.pdf \
	figures/generated/logistic-sigmoid-data.pdf \
	figures/generated/logistic-loss-geometry.pdf \
	figures/generated/logistic-validation-evidence.pdf \
	figures/generated/classification-performance-context.pdf \
	figures/generated/svm-hyperplane-geometry.pdf \
	figures/generated/linear-svm-margin.pdf \
	figures/generated/neural-network-anatomy.pdf \
	figures/generated/neural-composition-expressivity.pdf

.PHONY: all clean FORCE

all: $(OUTPUT_PDF)

$(OUTPUT_PDF): FORCE $(SOURCE) style/rice-dsm-book.sty $(FIGURES)
	mkdir -p $(BUILD_DIR) $(OUTPUT_DIR)
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=$(BUILD_DIR) $(SOURCE)
	cp $(BUILD_DIR)/textbook.pdf $(OUTPUT_PDF)

$(FIGURES): $(FIGURE_SCRIPT) ../data/course_datasets.sqlite
	cd .. && uv run python textbook/$(FIGURE_SCRIPT)

FORCE:

clean:
	$(LATEXMK) -C -outdir=$(BUILD_DIR) $(SOURCE)
	rm -f $(OUTPUT_PDF)
