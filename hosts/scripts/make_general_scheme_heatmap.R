#!/usr/bin/env Rscript
# ---------------------------------------------------------------------------
# host_general_scheme_R.png -- the general host scheme redrawn with
# ComplexHeatmap instead of matplotlib.
#
# This script does NO harmonization. Every number, every row, the >=5-tool
# species carve-out, the hierarchy blocks, the vector-fallback ("V") and
# multi-count ("*") flags and the per-tool breadth are produced by
# export_general_scheme_for_r.py, which in turn executes the existing
# make_general_scheme_heatmap.py. Re-deriving any of it here would let the two
# figures disagree silently, which is the one failure mode this project has
# repeatedly paid for.
#
#   python3 export_general_scheme_for_r.py && Rscript make_general_scheme_heatmap.R
#
# LAYOUT follows the matplotlib figure: paired bars on top, the grid, then the
# record/molecule track, rotated tool names on their prediction-target panel,
# and the A-F band. Legends sit in the right margin, each centred on the block
# it explains rather than packed into one stack.
#
# STYLING follows the reference figure the user supplied: rounded "pill" cells
# on a pale-grey bed instead of bordered squares, pale-tinted blocks with a
# coloured rule in place of saturated fills with reversed-out white text, and
# no boxes around the annotation panels.
#
# Requires: ComplexHeatmap (Bioconductor) >= 2.10 -- anno_barplot(beside=)
# is used for the grouped label-vs-category bars.
# ---------------------------------------------------------------------------
suppressPackageStartupMessages({
  library(ComplexHeatmap)
  library(grid)
  library(png)
})

.args <- commandArgs(trailingOnly = FALSE)
.f <- sub("^--file=", "", .args[grep("^--file=", .args)])
SC <- if (length(.f)) dirname(normalizePath(.f[1])) else getwd()
DATA <- file.path(SC, "r_general_scheme")
OUT <- file.path(dirname(SC), "host_general_scheme_R.png")

stopifnot(dir.exists(DATA))
mat_df <- read.csv(file.path(DATA, "matrix.csv"), check.names = FALSE)
rows   <- read.csv(file.path(DATA, "row_meta.csv"), colClasses = "character")
cols   <- read.csv(file.path(DATA, "col_meta.csv"), check.names = FALSE)
flags  <- read.csv(file.path(DATA, "cell_flags.csv"), colClasses = "character")
pal    <- read.csv(file.path(DATA, "palette.csv"), colClasses = "character")

rows$depth     <- as.integer(rows$depth)
rows$is_header <- as.integer(rows$is_header)
rows$italic    <- as.integer(rows$italic)

mat <- as.matrix(mat_df[, -1, drop = FALSE])
rownames(mat) <- mat_df$row_id
stopifnot(identical(rownames(mat), rows$row_id),
          identical(colnames(mat), cols$tool))

# ---- palette, taken from the Python figure rather than re-picked ----------
pget   <- function(kind, key) pal$value[pal$kind == kind & pal$key == key][1]
pmap   <- function(kind) setNames(pal$value[pal$kind == kind], pal$key[pal$kind == kind])
plabel <- function(kind) setNames(pal$extra[pal$kind == kind], pal$key[pal$kind == kind])

INK       <- pget("ink", "INK_PRIMARY")
INK2      <- pget("ink", "INK_SECONDARY")
BASELINE  <- pget("ink", "BASELINE")
PAGE      <- pget("ink", "PAGE")
SEQ_450   <- pget("ink", "SEQ_450")
SEQ_700   <- pget("ink", "SEQ_700")
CAT_RED   <- pget("ink", "CAT_RED")
CAT_MAG   <- pget("ink", "CAT_MAGENTA")

LINEAGE_ORDER <- pal$key[pal$kind == "lineage"]
LINEAGE_FULL  <- pmap("lineage")
ENDPOINT_COL  <- pmap("endpoint");      ENDPOINT_LAB <- plabel("endpoint")
RECTYPE_COL   <- pmap("record_type");   RECTYPE_LAB  <- plabel("record_type")
MOLTYPE_COL   <- pmap("molecule_type"); MOLTYPE_LAB  <- plabel("molecule_type")

N_CATS <- as.integer(pget("meta", "n_real_categories"))

# One tint ramp for the whole figure: the saturated hue wherever something has
# to be identified (border, label, bar, legend swatch), the same hue washed out
# wherever text or a number has to sit on top of it.
tint <- function(hex, amt) {
  m <- as.numeric(grDevices::col2rgb(hex)) / 255
  grDevices::rgb(m[1] + (1 - m[1]) * amt, m[2] + (1 - m[2]) * amt, m[3] + (1 - m[3]) * amt)
}
LINEAGE_PILL   <- vapply(LINEAGE_FULL, tint, "", amt = 0.68)
LINEAGE_BLOCK  <- vapply(LINEAGE_FULL, tint, "", amt = 0.80)
ENDPOINT_PANEL <- vapply(ENDPOINT_COL, tint, "", amt = 0.80)
EMPTY_CELL <- "#eef0ef"   # the pale bed an absent category sits on
PILL_R <- unit(1.5, "mm")

# ---------------------------------------------------------------------------
# Row labels. Species binomials are italic and everything above genus is not
# (publication requirement); the English gloss stays roman; header rows are
# bold. matplotlib needed mathtext for this, R needs plotmath -- built with
# bquote() so the names are never pasted into a parsed string.
#
# The indent on child rows is a trailing phantom(): row names are right-aligned
# against the heatmap, so invisible space on the RIGHT pushes the visible text
# left, which is what reads as "this belongs to the taxon above". Kept to
# two ems: four opened a corridor of dead white between the species labels and
# the grid, which is the widest thing on the figure that carries no meaning.
# ---------------------------------------------------------------------------
row_labels <- vector("expression", nrow(rows))
for (i in seq_len(nrow(rows))) {
  nm <- rows$name[i]
  e <- if (rows$is_header[i] == 1L) bquote(bold(.(nm)))
       else if (rows$italic[i] == 1L) bquote(italic(.(nm)))
       else bquote(plain(.(nm)))
  if (nzchar(rows$gloss[i])) {
    g <- paste0(" (", rows$gloss[i], ")")
    e <- if (rows$is_header[i] == 1L) bquote(.(e) * bold(.(g))) else bquote(.(e) * plain(.(g)))
  }
  if (rows$depth[i] > 0L) e <- bquote(.(e) * phantom("MM"))
  row_labels[[i]] <- e
}
row_label_col <- unname(LINEAGE_FULL[rows$lineage])
# One coordinated type scale. Sizes here drive the geometry below (row height
# from ROW_FS, cell width from the widest number at CELL_FS), so raising a size
# and leaving the box alone cannot silently clip anything.
ROW_FS  <- 13.5   # row labels
ROW_MM  <- 6.0    # mm per row: ~4.8mm of that is glyph, the rest leading
CELL_FS <- 8.6    # numbers in the cells
CELL_MM <- 13.0   # mm per column; checked against the widest number below
PANEL_FS <- 13.5  # lineage-panel name; ALSO sizes the transparent row_title
                  # that reserves the panel, so the two must not drift apart
LGD_LAB <- gpar(fontsize = 12.5)
LGD_TIT <- gpar(fontsize = 13.5, fontface = "bold")

# The column width is set by hand but constrained by the widest number that has
# to sit inside a pill. Measured rather than estimated: a cell narrowed past
# this clips the digits, and nothing else in the pipeline would notice.
.widest <- format(max(mat), big.mark = ",", trim = TRUE)
.need <- convertWidth(grobWidth(textGrob(.widest, gp = gpar(fontsize = CELL_FS,
                                                            fontface = "bold"))),
                      "mm", valueOnly = TRUE)
.have <- CELL_MM - 1.1                       # the pill insets by this much
if (.need > .have) {
  stop(sprintf("CELL_MM=%.1f leaves %.1fmm inside the pill but \"%s\" needs %.1fmm at %.1fpt -- widen the column or shrink CELL_FS",
               CELL_MM, .have, .widest, .need, CELL_FS))
}
message(sprintf("widest cell number \"%s\": %.1fmm of %.1fmm available", .widest, .need, .have))

lineage_split  <- factor(rows$lineage, levels = LINEAGE_ORDER)
endpoint_split <- factor(cols$endpoint_id, levels = unique(cols$endpoint_id))
row_slices <- split(seq_len(nrow(mat)), lineage_split)
col_slices <- split(seq_len(ncol(mat)), endpoint_split)

# The lineage side panel is the matplotlib figure's: a narrow saturated stripe,
# a divider rule, the icon, then the name set HORIZONTALLY in black -- not a
# filled block with rotated reversed-out type. Horizontal type also means a
# one-row slice can carry its name, so every lineage is labelled, as in Python.
#
# ComplexHeatmap has no way to compose that inside a row title, so the title is
# used only to RESERVE the width: the string is padded and drawn transparent,
# and the four real elements are painted into the reserved strip by
# decorate_row_title() further down.
LINEAGE_TITLE <- setNames(LINEAGE_ORDER, LINEAGE_ORDER)
LINEAGE_TITLE["Non-mammalian vertebrates"] <- "Non-mammalian\nvertebrates"
# One line, and just "Unknown". Excluded records never reach this figure --
# build_species_matrix.py drops every Status=EXCL row before the species matrix
# exists -- so the second half of the registry name promised content that is not
# drawn. The wrap it needed was also the only two-line name in a one-row slice,
# which is where the panel and the row labels met.
LINEAGE_TITLE["Unknown/Excluded"] <- "Unknown"
# NOT wrapped, though it is the longest name here. Its slice is one row tall and
# so are the four around it, and a two-line name in a 6mm slot overruns its
# neighbours on both sides -- the panel does not clip. The block is widened to
# hold it on one line instead, which the pad calibration does on its own.

# The name and its icon are set flush RIGHT, against the row labels, not flush
# left behind the stripe. The row labels are themselves right-aligned, so a
# left-aligned panel opened a corridor as wide as the difference between
# "Non-mammalian vertebrates" and "Fungi" -- 28mm of white at "Mammals". Flush
# right gives every lineage the same small gap, and makes an overlap with the
# labels structurally impossible: they are drawn in the next block along, and
# the panel never crosses into it.
PANEL_STRIPE_W <- 3.0   # the saturated lineage stripe, at the block's left edge
PANEL_RULE_X   <- 4.8   # the divider, which reads as one continuous rule
PANEL_ICON_X   <- 6.4   # the icon never starts left of this
PANEL_ICON_W   <- 6.2   # its widest; a short slice gets a smaller glyph
PANEL_ICON_GAP <- 1.4   # icon to name
PANEL_GAP      <- 2.0   # name to the row labels

.tw <- function(s) convertWidth(grobWidth(textGrob(s, gp = gpar(fontsize = PANEL_FS,
                                                                fontface = "bold"))),
                                "mm", valueOnly = TRUE)
# Measured on a scratch png device, not on whatever R opens by default: the two
# disagree by about 7%, which here means reserving 2.6mm of panel that nothing
# ever draws into. Canvas size is irrelevant to text metrics; device type is not.
.on_png <- function(f) {
  tmp <- tempfile(fileext = ".png")
  png(tmp, width = 6, height = 6, units = "in", res = 400, bg = "white")
  on.exit({ dev.off(); unlink(tmp) }, add = TRUE)
  f()
}
TITLE_W_MAX <- .on_png(function() max(vapply(LINEAGE_TITLE, .tw, 0)))
SPACE_MM    <- .on_png(function() .tw("M M") - .tw("MM"))
PANEL_W <- PANEL_ICON_X + PANEL_ICON_W + PANEL_ICON_GAP + TITLE_W_MAX + PANEL_GAP

# The block is only as wide as the panel needs. Its width comes from the width
# of the (invisible) title, so it is bought with leading spaces -- and the
# number of them is calibrated against the drawn block below rather than
# guessed, because guessing it is what left the corridor in the first place.
row_titles_for <- function(pad_n) paste0(strrep(" ", pad_n), LINEAGE_TITLE)
PAD_N <- max(0, round((PANEL_W - TITLE_W_MAX) / SPACE_MM))

# Lineage icons, rasterised from the emoji font by the Python exporter -- see
# export_general_scheme_for_r.py. Drawn into the row-title block below.
ICON_DIR <- file.path(DATA, "icons")
.slug <- function(s) gsub(" ", "_", gsub("/", "_", tolower(s)))
LINEAGE_ICON <- lapply(setNames(LINEAGE_ORDER, LINEAGE_ORDER), function(g) {
  f <- file.path(ICON_DIR, paste0(.slug(g), ".png"))
  if (file.exists(f)) png::readPNG(f) else NULL
})

# One glyph per hierarchy header, from the same exporter. The exporter asserts
# that every header has one, so a missing file here means the icons are stale
# rather than that some header is legitimately unillustrated -- say so loudly.
TAXON_ICON <- lapply(setNames(nm = rows$name[rows$is_header == 1L]), function(t) {
  f <- file.path(ICON_DIR, paste0("taxon_", .slug(t), ".png"))
  if (!file.exists(f)) stop("no taxon icon for '", t, "' -- rerun export_general_scheme_for_r.py")
  png::readPNG(f)
})

# ---------------------------------------------------------------------------
# Cells are coloured by LINEAGE, not by value -- this is a presence/exact-count
# grid, not a continuous scale, so the built-in colour mapping is bypassed
# entirely (rect_gp type="none") and each cell is drawn in cell_fun.
# ---------------------------------------------------------------------------
vflag <- matrix(FALSE, nrow(mat), ncol(mat), dimnames = dimnames(mat))
if (nrow(flags)) vflag[cbind(flags$row_id, flags$tool)] <- TRUE

cell_fun <- function(j, i, x, y, w, h, fill) {
  # A header carries no data. It gets no pill at all -- an empty-bed pill would
  # read as "absent from every tool", the opposite of what a header means.
  if (rows$is_header[i] == 1L) return(invisible(NULL))
  v <- mat[i, j]
  lin <- rows$lineage[i]
  ww <- w - unit(1.1, "mm"); hh <- h - unit(0.7, "mm")
  if (v > 0) {
    grid::grid.roundrect(x, y, ww, hh, r = PILL_R,
                         gp = gpar(fill = LINEAGE_PILL[[lin]],
                                   col = LINEAGE_FULL[[lin]], lwd = 1.0))
    grid::grid.text(formatC(v, format = "d", big.mark = ","), x, y,
                    gp = gpar(fontsize = CELL_FS, fontface = "bold", col = INK))
    if (vflag[i, j]) {
      bx <- x + w * 0.33; by <- y + h * 0.29
      grid::grid.circle(bx, by, r = unit(1.4, "mm"), gp = gpar(fill = CAT_MAG, col = NA))
      grid::grid.text("V", bx, by, gp = gpar(fontsize = 6.5, fontface = "bold", col = "white"))
    }
  } else {
    grid::grid.roundrect(x, y, ww, hh, r = PILL_R, gp = gpar(fill = EMPTY_CELL, col = NA))
  }
}

# ---------------------------------------------------------------------------
# Top: how many labels the study itself reports vs how many of the harmonized
# categories its data populate. Vector-fallback cells are already excluded from
# `breadth` upstream.
# ---------------------------------------------------------------------------
# One bar, not two. The second used to be "labels the study reports", taken from
# the curation workbook: of its 278 rows only 38 carry a pointer into an
# article, 174 are the release's own labels reproduced by the recompute, and 48
# match on count alone. It did not measure what its name said.
bars <- cbind(`Host categories populated` = cols$breadth)
# Bars are a MEASUREMENT, not a category, so they get their own neutral pair
# rather than another hue: any colour here would read as a seventh lineage or a
# seventh tool group. SEQ_450 used to fill the blue bar and is one shade off the
# Mammals blue, which made the comparison look like a mammal row.
BAR_REPORTED  <- "#5d1a2e"   # what the study itself reports. Not a grey: a
                             # neutral pair read as "no data here", which is
                             # what the empty cells in the grid already say.
                             # The yellow is free now that Plants took the
                             # turquoise, and it belongs to no lineage.
BAR_POPULATED <- "#4a4a48"   # what its data actually populate. Was a blue
                             # slate; at 62% on white that became #878e96, which
                             # is 16 units from the Unknown/Excluded lineage
                             # swatch #78909c -- effectively the same colour in
                             # the legend stack. Neutral graphite instead.

TOOL_FS <- 13
# Rotated names, so their column height is the longest name's rendered WIDTH.
# +5mm buys the multi-count mark its place at the top of the panel.
TOOL_PANEL_H <- max_text_width(cols$tool, gp = gpar(fontsize = TOOL_FS, fontface = "bold")) +
                unit(5.5, "mm")

top_anno <- HeatmapAnnotation(
  # Drawn by hand below, not by anno_barplot: that cannot round a bar's top
  # corners, and its axis is drawn in its own grey.
  bars = anno_empty(border = FALSE, height = unit(2.5, "cm")),
  annotation_name_gp = gpar(fontsize = 0), annotation_label = ""
)

# ---------------------------------------------------------------------------
# Bottom: the per-tool metadata tracks, then the tool names, then the
# prediction-target band. Column names are drawn as an explicit anno_text
# rather than by show_column_names, so their position in this stack is fixed
# instead of depending on ComplexHeatmap's component order.
# ---------------------------------------------------------------------------
bottom_anno <- HeatmapAnnotation(
  # One small square per tool rather than a full-width bar: anno_simple paints
  # the whole column and the two tracks then read as continuous ribbons whose
  # colour changes are hard to attribute to a particular tool.
  # Both tracks on ONE row, two squares side by side per tool, as the
  # matplotlib figure does it -- stacking them cost a whole extra band of
  # height for information that reads just as well side by side.
  `record / molecule type` = anno_empty(border = FALSE, height = unit(5.4, "mm")),
  # The tool names sit ON their prediction-target panel, as in the reference,
  # rather than as bare text above a separate band. Drawn by hand (anno_empty +
  # decoration below) because anno_text cannot carry a per-group background.
  # The A-F band underneath is butted straight against it, gap 0 and no border
  # on either, so panel and band read as one tinted block per group.
  #
  # Height measured from the longest name rather than fixed: a hand-picked
  # 4.4cm left more than a centimetre of empty panel under every tool, and on a
  # figure this tall that is height spent on nothing. The multi-count mark now
  # rides inside the panel too, which retires a whole annotation band.
  tool = anno_empty(border = FALSE, height = TOOL_PANEL_H),
  target = anno_block(gp = gpar(fill = ENDPOINT_PANEL[levels(endpoint_split)], col = NA),
                      labels = levels(endpoint_split),
                      labels_gp = gpar(fontsize = 13.5, fontface = "bold",
                                       col = ENDPOINT_COL[levels(endpoint_split)]),
                      height = unit(6, "mm")),
  annotation_name_side = "left",
  annotation_name_gp = gpar(fontsize = 11.5, fontface = "bold", col = INK),
  # Positional, not named: a name containing "/" does not match as a key here
  # and the label silently vanished.
  show_annotation_name = c(TRUE, FALSE, FALSE),
  gap = unit(c(1.5, 0), "mm")
)

# ---------------------------------------------------------------------------
# A narrow empty channel between the row labels and the grid, decorated below
# with the header -> children connectors. Bold type and an indent alone did not
# read as a hierarchy at a glance in the matplotlib version either.
# ---------------------------------------------------------------------------
left_anno <- rowAnnotation(
  tree = anno_empty(border = FALSE, width = unit(4, "mm")),
  show_annotation_name = FALSE
)

build_ht <- function(pad_n) Heatmap(
  mat,
  name = "count",
  col = c("0" = EMPTY_CELL),     # unused: rect_gp type="none" bypasses it
  rect_gp = gpar(type = "none"),
  cell_fun = cell_fun,
  cluster_rows = FALSE, cluster_columns = FALSE,
  row_order = seq_len(nrow(mat)), column_order = seq_len(ncol(mat)),
  row_split = lineage_split, column_split = endpoint_split,
  # No gap between lineage slices: the row rhythm has to stay uniform all the
  # way down, exactly as within a slice. The lineage boundary is carried by the
  # coloured block and its icon, not by a hole in the grid. Columns keep their
  # gap -- there the groups genuinely are separate panels.
  row_gap = unit(0, "mm"), column_gap = unit(3.4, "mm"),
  row_title = row_titles_for(pad_n), row_title_rot = 0,
  row_title_gp = gpar(col = "transparent", fontface = "bold", fontsize = PANEL_FS),
  column_title = NULL,
  row_labels = row_labels, row_names_side = "left",
  row_names_gp = gpar(fontsize = ROW_FS, col = INK),
  # Row height pinned too, for the same reason as the width: left to fill the
  # canvas, 59 rows were given ~6.1mm each against 3.7mm of type, and that
  # slack alone made the figure several inches taller than a page wants.
  height = unit(nrow(mat) * ROW_MM, "mm"),
  # Measured, not left to the default: ComplexHeatmap under-allocates the row
  # name strip for plotmath expressions, which silently truncated the longest
  # binomials ("Chlorocebus aethiops" lost its first two letters). The width
  # also has to hold the taxon names set beside the block first members.
  row_names_max_width = max_text_width(row_labels, gp = gpar(fontsize = ROW_FS)) +
                        unit(4, "mm"),
  show_column_names = FALSE,
  # Body width pinned rather than left to fill the canvas: with only 14 columns
  # the default stretched each cell to ~24mm against a ~6mm row, so the grid
  # read as a set of wide bars instead of a matrix. 13mm still clears the
  # widest number on the figure ("136,031").
  width = unit(ncol(mat) * CELL_MM, "mm"),
  left_annotation = left_anno,
  top_annotation = top_anno, bottom_annotation = bottom_anno,
  show_heatmap_legend = FALSE,
  border = FALSE, use_raster = FALSE
)

# ---------------------------------------------------------------------------
# Legends -- same five blocks, same order, same side as the matplotlib figure.
# ---------------------------------------------------------------------------
lgd_cell <- Legend(labels_gp = LGD_LAB, title_gp = LGD_TIT, 
  title = "Cell = resolution",
  labels = c("Exact count (coloured by lineage)", "Not present",
             "V = vector, not host",
             "* = this tool can count one\nrecord in several rows"),
  legend_gp = gpar(fill = c(LINEAGE_PILL[["Mammals"]], EMPTY_CELL, CAT_MAG, CAT_RED)),
  border = c(LINEAGE_FULL[["Mammals"]], NA, NA, NA)
)
lgd_lineage <- Legend(labels_gp = LGD_LAB, title_gp = LGD_TIT, title = "Lineage", labels = LINEAGE_ORDER,
                      legend_gp = gpar(fill = unname(LINEAGE_FULL[LINEAGE_ORDER])))
lgd_rec <- Legend(labels_gp = LGD_LAB, title_gp = LGD_TIT, title = "Record type", labels = unname(RECTYPE_LAB[names(RECTYPE_COL)]),
                  legend_gp = gpar(fill = unname(RECTYPE_COL)))
lgd_mol <- Legend(labels_gp = LGD_LAB, title_gp = LGD_TIT, title = "Molecule type", labels = unname(MOLTYPE_LAB[names(MOLTYPE_COL)]),
                  legend_gp = gpar(fill = unname(MOLTYPE_COL)))
lgd_target <- Legend(labels_gp = LGD_LAB, title_gp = LGD_TIT, title = "Prediction target",
                     # Wrapped by measure, not by hand: these are the widest
                     # strings on the figure and they set the whole right margin.
                     labels = paste0(names(ENDPOINT_COL), "  ",
                                     sub("(.{24,}?) ", "\\1\n   ", ENDPOINT_LAB[names(ENDPOINT_COL)])),
                     # Saturated in the legend, pale on the band itself -- the
                     # legend is where the six colours have to be told apart.
                     legend_gp = gpar(fill = unname(ENDPOINT_COL)))
# ---------------------------------------------------------------------------
# The canvas. Height is free, width is not: the layout has a fixed width of its
# own -- pinned body, measured row names, the strip reserved for the lineage
# panel, the 92mm legend margin -- and ComplexHeatmap CENTRES that block on the
# page. A page narrower than the block therefore overflows off BOTH edges, and
# on the left that costs the lineage panel its stripe, its rule and its icon
# while the run still exits 0 and the names, sitting further right, still look
# correct. Narrowing the columns did exactly this once.
#
# So the layout is drawn once to a null device purely to ask where the panel
# lands, and the script refuses to render a page it does not fit on. Centred
# means a page 1mm wider moves the left edge only 0.5mm, hence the doubling.
# ---------------------------------------------------------------------------
FIG_W <- 19.12                          # inches; fits 16 tool columns, the fit check below adjusts it
FIG_H <- 17.6
PADDING <- unit(c(4, 4, 4, 92), "mm")   # bottom, left, top, right
PAD_L <- 4

# Measured on a png device, not on pdf(NULL): the two disagree on font metrics
# by enough to move this by 1.6mm, and it is the png that has to fit. The
# throwaway render is the price of the check. Returns the panel block's left
# edge and its width, both in mm on the page.
panel_block_mm <- function(ht, w_in) {
  tmp <- tempfile(fileext = ".png")
  png(tmp, width = w_in, height = FIG_H, units = "in", res = 400, bg = PAGE)
  on.exit({ dev.off(); unlink(tmp) }, add = TRUE)
  draw(ht, show_annotation_legend = FALSE, padding = PADDING)
  out <- c(left = NA_real_, width = NA_real_)
  decorate_row_title("count", slice = 1, {
    out <<- c(left = deviceLoc(unit(0, "npc"), unit(0, "npc"), valueOnly = TRUE)$x * 25.4,
              width = convertWidth(unit(1, "npc"), "mm", valueOnly = TRUE))
  })
  out
}

# The reserved block is bought in spaces, and a space is not a unit anyone can
# reason about: what the pad measures at PANEL_FS is not what ComplexHeatmap
# then adds around the title. So the pad is calibrated against the block that
# actually got drawn, and converges in a step or two.
ht <- build_ht(PAD_N)
.blk <- panel_block_mm(ht, FIG_W)
for (.i in 1:3) {
  .step <- round((PANEL_W - .blk[["width"]]) / SPACE_MM)
  if (abs(.blk[["width"]] - PANEL_W) <= 0.4 || .step == 0) break
  PAD_N <- max(0, PAD_N + .step)
  ht <- build_ht(PAD_N)
  .blk <- panel_block_mm(ht, FIG_W)          # always the block `ht` will draw
}
message(sprintf("lineage panel: %.1fmm needed, %.1fmm reserved by %d spaces",
                PANEL_W, .blk[["width"]], PAD_N))

# The block's width changes with the layout (it shrank by one column when
# HostClassifier was excluded) and with the font metrics of the machine that
# draws it, so FIG_W is a starting value, not a constant: the page is resized
# until the panel sits PAD_L from the edge (the block is centred, hence the
# doubling). Only a layout that still does not fit after that stops the run.
.x0 <- .blk[["left"]]
for (.j in 1:3) {
  if (is.finite(.x0) && abs(.x0 - PAD_L) <= 0.5) break
  if (!is.finite(.x0)) break
  FIG_W <- FIG_W + 2 * (PAD_L - .x0) / 25.4
  .blk <- panel_block_mm(ht, FIG_W)
  .x0 <- .blk[["left"]]
  message(sprintf("page width adjusted to %.2f in to fit the layout", FIG_W))
}
if (!is.finite(.x0) || abs(.x0 - PAD_L) > 0.5) {
  stop(sprintf("the lineage panel starts %.1fmm from the page edge, not %.1fmm, at FIG_W = %.2f in",
               .x0, PAD_L, FIG_W))
}
message(sprintf("layout fits: lineage panel starts %.1fmm from the page edge", .x0))

# 400 dpi, not 220: this is meant for print, where journals ask 300+ for
# combination line/text art. The layout is unchanged by it -- every size in
# this script is in mm or points, so the raster just resolves finer.
png(OUT, width = FIG_W, height = FIG_H, units = "in", res = 400, bg = PAGE)
# No legend list. One packed block put every key the same distance from
# everything and left two thirds of the right-hand column empty; each legend is
# instead drawn against the element it explains, into the margin reserved by
# the last entry of `padding` (order: bottom, left, top, right).
draw(ht, show_annotation_legend = FALSE, padding = PADDING)

# ---- legends, each centred on the block it explains ------------------------
# Decoration viewports do not clip, so a legend drawn past an element's right
# edge lands in the reserved margin at that element's own height. Three groups,
# each centred on its part of the figure rather than aligned to an edge.
#
# record/molecule describe the grid's COLUMNS, so their keys belong with the
# cell and lineage keys in the heatmap group, not down with the tool panel.
# just is given numerically: ComplexHeatmap's Legend draw method accepts
# "center" but silently draws NOTHING for the British "centre", which is a
# very quiet way to lose every legend on the figure.
LGD_X <- unit(1, "npc") + unit(8, "mm")
.last <- length(col_slices)
# Row gap is zero, so the body is exactly nrow * the pinned row height and its
# centre can be measured off the first slice's top edge.
BODY_HALF <- unit(nrow(mat) * ROW_MM / 2, "mm")

lgd_heatmap <- packLegend(lgd_cell, lgd_lineage, lgd_rec, lgd_mol,
                          direction = "vertical", gap = unit(7, "mm"))

# The bars carry one quantity, so they get a title rather than a one-entry key.
decorate_annotation("bars", slice = .last, {
  grid.text("Categories populated", x = LGD_X, y = unit(0.5, "npc"),
            just = c(0, 0.5), gp = LGD_TIT)
})

decorate_heatmap_body("count", row_slice = 1, column_slice = .last, {
  draw(lgd_heatmap, x = LGD_X, y = unit(1, "npc") - BODY_HALF,
       just = c(0, 0.5))
})

# Centred on the name panel and the A-F band together, which is the one block
# the prediction-target key explains.
decorate_annotation("tool", slice = .last, {
  draw(lgd_target, x = LGD_X, y = unit(0.5, "npc") - unit(3, "mm"),
       just = c(0, 0.5))
})

# ---- taxon brackets --------------------------------------------------------
# With the header rows gone the taxon is carried here: a "[" spanning its
# members with the name set inside it, one level in from the lineage panel and
# in the same idiom. Per-row arms are deliberately not drawn -- they would run
# straight through the rotated name.
#
# The bracket is pushed LEFT out of its channel by exactly the indent, so it
# lands where the indented species labels end rather than a full indent clear
# of them. Decoration viewports do not clip, so the negative offset is legal;
# the indent is measured, not assumed, so it tracks the phantom() in the labels
# if the font size ever changes.
INDENT_MM <- convertWidth(grobWidth(textGrob("MM", gp = gpar(fontsize = ROW_FS))),
                          "mm", valueOnly = TRUE)
SPINE_X <- unit(0, "npc") - unit(INDENT_MM - 1.3, "mm")

for (k in seq_along(row_slices)) {
  idx <- row_slices[[k]]
  n <- length(idx)
  if (!n) next
  ycent <- function(pos) unit(1 - (pos - 0.5) / n, "npc")
  decorate_annotation("tree", slice = k, {
    for (p in seq_len(n)) {
      if (rows$is_header[idx[p]] != 1L) next
      # Icon immediately left of the header's own text. No width is reserved
      # for it: every header label is shorter than the widest species label,
      # which is what sets the strip, so the slack is already there.
      img <- TAXON_ICON[[rows$name[idx[p]]]]
      if (!is.null(img)) {
        wlab <- convertWidth(grobWidth(textGrob(row_labels[[idx[p]]],
                                                gp = gpar(fontsize = ROW_FS))),
                             "mm", valueOnly = TRUE)
        ih <- 5.3; iw <- ih * dim(img)[2] / dim(img)[1]
        grid.raster(img, x = unit(0, "npc") - unit(wlab + 1.8 + iw / 2, "mm"),
                    y = ycent(p), width = unit(iw, "mm"), height = unit(ih, "mm"))
      }
      kids <- integer(0)
      q <- p + 1L
      while (q <= n && rows$depth[idx[q]] == 1L) { kids <- c(kids, q); q <- q + 1L }
      if (!length(kids)) next
      grid.segments(SPINE_X, ycent(p) - unit(1.2, "mm"),
                    SPINE_X, ycent(max(kids)),
                    gp = gpar(col = INK2, lwd = 1.2))
      for (q in kids) {
        grid.segments(SPINE_X, ycent(q), unit(0.92, "npc"), ycent(q),
                      gp = gpar(col = INK2, lwd = 1.2))
      }
    }
  })
}

# ---- lineage side panel: stripe | divider | icon | name --------------------
# Same four elements, same order, as the matplotlib figure. The stripe and the
# rule stay at the block's left edge -- they are a spine, and with row_gap at 0
# the per-slice segments meet and read as the single continuous rule Python
# draws in one go. The icon and the name are set against the block's RIGHT edge
# instead, so they sit as close to the row labels as they can without ever
# entering their block.
for (k in seq_along(row_slices)) {
  lin <- names(row_slices)[k]
  img <- LINEAGE_ICON[[lin]]
  decorate_row_title("count", slice = k, {
    grid.rect(unit(0, "npc"), unit(0.5, "npc"),
              width = unit(PANEL_STRIPE_W, "mm"), height = unit(1, "npc") - unit(0.5, "mm"),
              just = "left", gp = gpar(fill = LINEAGE_FULL[[lin]], col = NA))
    grid.segments(unit(PANEL_RULE_X, "mm"), unit(0, "npc"),
                  unit(PANEL_RULE_X, "mm"), unit(1, "npc"),
                  gp = gpar(col = BASELINE, lwd = 1))
    bw <- convertWidth(unit(1, "npc"), "mm", valueOnly = TRUE)
    tx <- bw - PANEL_GAP                       # right edge of the name
    grid.text(LINEAGE_TITLE[[lin]], x = unit(tx, "mm"), y = unit(0.5, "npc"),
              just = c(1, 0.5), gp = gpar(fontsize = PANEL_FS, fontface = "bold", col = INK),
              vp = viewport(clip = "off"))
    if (!is.null(img)) {
      # Sized against the slice actually rendered: Plants and Fungi are one row
      # tall, and a fixed glyph height would overflow them.
      bh <- convertHeight(unit(1, "npc"), "mm", valueOnly = TRUE)
      aspect <- dim(img)[1] / dim(img)[2]        # rows/cols = height/width
      iw <- min(PANEL_ICON_W, (0.82 * bh) / aspect)
      # Rides with the name rather than at a fixed x, so the two stay one unit;
      # floored at the spine so a long name cannot push it onto the rule.
      ix <- max(PANEL_ICON_X, tx - .tw(LINEAGE_TITLE[[lin]]) - PANEL_ICON_GAP - iw)
      if (iw >= 1.2) {
        grid.raster(img, x = unit(ix + iw / 2, "mm"), y = unit(0.5, "npc"),
                    width = unit(iw, "mm"), height = unit(iw * aspect, "mm"))
      }
    }
  })
}

# ---- tinted prediction-target panel behind the tool names ------------------
# Only the top corners are rounded: the bottom edge has to meet the A-F band
# squarely, or a rounded corner would open a notch between the two.
for (k in seq_along(col_slices)) {
  jj <- col_slices[[k]]
  cid <- names(col_slices)[k]
  decorate_annotation("tool", slice = k, {
    grid.rect(unit(0.5, "npc"), unit(0, "npc"),
              width = unit(1, "npc") + unit(1.2, "mm"), height = unit(0.965, "npc"),
              just = "bottom", gp = gpar(fill = ENDPOINT_PANEL[[cid]], col = NA))
    grid.roundrect(unit(0.5, "npc"), unit(0.965, "npc") - unit(2, "mm"),
                   width = unit(1, "npc") + unit(1.2, "mm"),
                   height = unit(4, "mm"), r = unit(2, "mm"),
                   just = "bottom", gp = gpar(fill = ENDPOINT_PANEL[[cid]], col = NA))
    for (p in seq_along(jj)) {
      grid.text(cols$tool[jj[p]], x = unit(p, "native"), y = unit(0, "npc") + unit(1.4, "mm"),
                rot = 90, just = "left",
                gp = gpar(fontsize = TOOL_FS, fontface = "bold", col = INK))
      # Rides at the top of the panel instead of on an annotation row of its
      # own -- one band of height saved, and it sits nearer the tool it marks.
      if (cols$double_count[jj[p]] == 1) {
        grid.text("*", x = unit(p, "native"), y = unit(1, "npc") - unit(0.8, "mm"),
                  just = "top", gp = gpar(fontsize = 19, fontface = "bold", col = CAT_RED))
      }
    }
  })
}

# ---- record / molecule squares, two per tool on one row --------------------
for (k in seq_along(col_slices)) {
  jj <- col_slices[[k]]
  decorate_annotation("record / molecule type", slice = k, {
    # anno_empty carries no data and so draws no annotation name of its own --
    # unlike anno_points, which is why the label disappeared when the two
    # tracks were merged onto one row. Drawn here against the first slice.
    if (k == 1) {
      grid.text("record / molecule type", x = unit(0, "npc") - unit(2, "mm"),
                y = unit(0.5, "npc"), just = "right",
                gp = gpar(fontsize = 11.5, fontface = "bold", col = INK))
    }
    for (p in seq_along(jj)) {
      # Softened corners rather than hard squares, to match the pills; the
      # column is 14.5mm wide, so the pair has room to be read at a glance.
      grid.roundrect(unit(p, "native") - unit(1.7, "mm"), unit(0.5, "npc"),
                     width = unit(3, "mm"), height = unit(3, "mm"), r = unit(0.6, "mm"),
                     just = "centre",
                     gp = gpar(fill = RECTYPE_COL[[cols$record_type[jj[p]]]], col = NA))
      grid.roundrect(unit(p, "native") + unit(1.7, "mm"), unit(0.5, "npc"),
                     width = unit(3, "mm"), height = unit(3, "mm"), r = unit(0.6, "mm"),
                     just = "centre",
                     gp = gpar(fill = MOLTYPE_COL[[cols$molecule_type[jj[p]]]], col = NA))
    }
  })
}

# ---- the paired bars, their axis and their values --------------------------
# anno_empty gives no y scale, so values are mapped to npc against a shared
# YMAX; the 1.16 leaves headroom for the number printed above each bar.
YMAX <- max(bars, na.rm = TRUE) * 1.16
BAR_W <- 0.62          # native units, i.e. fraction of one column
BAR_R <- unit(1.1, "mm")
# Lightened by compositing onto the page ONCE, not by drawing translucent.
# A bar is two overlapping shapes (rounded body + squared-off foot), and with
# real alpha the overlap doubles up: every bar came out with a visible seam,
# its top cap paler than its body. Blending here is the same result on a white
# page and has no overlap to compound.
# One alpha for both bars put them 43 units apart -- below the ~60 at which two
# fills stop reading as different, and this is the one comparison the figure
# asks the reader to make on every column. Lightening only the burgundy gives a
# light/dark pair instead: 193 apart, and each at least 78 from every lineage
# and prediction-target colour.
BAR_ALPHA <- c(0.35, 1.00)
BAR_FILL <- c(tint(BAR_POPULATED, 1 - BAR_ALPHA[2]))

for (k in seq_along(col_slices)) {
  jj <- col_slices[[k]]
  decorate_annotation("bars", slice = k, {
    if (k == 1) {
      ticks <- pretty(c(0, max(bars)), n = 3)
      ticks <- ticks[ticks <= YMAX]
      grid.segments(unit(0, "npc") - unit(2.5, "mm"), unit(0, "npc"),
                    unit(0, "npc") - unit(2.5, "mm"), unit(max(ticks) / YMAX, "npc"),
                    gp = gpar(col = INK, lwd = 1.1))
      for (tv in ticks) {
        grid.segments(unit(0, "npc") - unit(3.6, "mm"), unit(tv / YMAX, "npc"),
                      unit(0, "npc") - unit(2.5, "mm"), unit(tv / YMAX, "npc"),
                      gp = gpar(col = INK, lwd = 1.1))
        grid.text(tv, unit(0, "npc") - unit(4.4, "mm"), unit(tv / YMAX, "npc"),
                  just = c("right", "centre"),
                  gp = gpar(fontsize = 10.5, col = INK))
      }
    }
    for (p in seq_along(jj)) {
      for (b in 1) {
        v <- bars[jj[p], b]
        # NA, not 0: a study that enumerates no host labels gets no bar and no
        # number, because a drawn "0" claims it reports none of them.
        if (is.na(v)) next
        x <- unit(p, "native")
        h <- unit(v / YMAX, "npc")
        # Rounded all round, then the lower part squared off again, so only the
        # top corners are soft and the bar still sits flat on the axis. The
        # radius is capped at half the bar's own height: at the full 1.1mm a
        # short bar (MENB's 3, DeepHoF's 5) came out a floating capsule with a
        # rounded bottom too, clear of the baseline.
        r <- unit(min(1.1, convertHeight(h, "mm", valueOnly = TRUE) / 2), "mm")
        grid.roundrect(x, unit(0, "npc"), width = unit(BAR_W, "native"), height = h,
                       r = r, just = "bottom",
                       gp = gpar(fill = BAR_FILL[b], col = NA))
        grid.rect(x, unit(0, "npc"), width = unit(BAR_W, "native"),
                  height = h - r, just = "bottom",
                  gp = gpar(fill = BAR_FILL[b], col = NA))
        grid.text(v, x, h + unit(1.2, "mm"), just = "bottom",
                  gp = gpar(fontsize = CELL_FS, fontface = "bold", col = INK))
      }
    }
  })
}

invisible(dev.off())
cat("saved", OUT, "|", N_CATS, "categories +", sum(rows$is_header), "header rows\n")
