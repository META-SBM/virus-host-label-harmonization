#!/usr/bin/env Rscript

# Render the publication taxonomic-breadth figure with ComplexHeatmap.

suppressPackageStartupMessages({
  library(ComplexHeatmap)
  library(grid)
})

script_argument <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
if (length(script_argument) != 1L) {
  stop("Cannot determine the path to plot_order_figure.R", call. = FALSE)
}
script_path <- normalizePath(sub("^--file=", "", script_argument), mustWork = TRUE)
package_root <- normalizePath(dirname(script_path), mustWork = TRUE)

tables_dir <- file.path(package_root, "outputs", "tables")
data_dir <- file.path(package_root, "data", "intermediate")
config_dir <- file.path(package_root, "config")
main_figures_dir <- file.path(package_root, "outputs", "figures", "main")

family_presence_path <- file.path(
  tables_dir,
  "family_presence_eukaryotic.csv"
)
ictv_reference_path <- file.path(data_dir, "ictv_family_reference.csv")
tool_metadata_path <- file.path(config_dir, "tools.csv")

excluded_tools <- character(0)

genome_classes <- c(
  "dsDNA",
  "ssDNA",
  "dsRNA",
  "(+)ssRNA",
  "(−)ssRNA",
  "reverse-transcribing"
)
genome_class_titles <- c("dsDNA", "ssDNA", "dsRNA", "(+)ssRNA", "(-)ssRNA", "RT")
genome_class_display <- c(
  "dsDNA", "ssDNA", "dsRNA", "(+)ssRNA", "(-)ssRNA", "reverse-transcribing"
)
names(genome_class_titles) <- genome_classes
names(genome_class_display) <- genome_classes
genome_colors <- c(
  "dsDNA" = "#0B575DFF",
  "ssDNA" = "#2C7AA1FF",
  "dsRNA" = "#BA0C2FFF",
  "(+)ssRNA" = "#48448EFF",
  "(−)ssRNA" = "#F84A28FF",
  "reverse-transcribing" = "#0033A0FF"
)
endpoint_colors <- c(
  "Host-taxon classification" = "#3B82C4",
  "Virus–host association scoring" = "#35A86B",
  "Reservoir or vector prediction" = "#D9A800",
  "Human-infectivity prediction" = "#E05A67",
  "Host-adaptation scoring" = "#8061C9",
  "Spillover-risk prioritization" = "#20A8B5"
)
endpoint_display <- c(
  "Host-taxon classification" = "Host-taxon\nclassification",
  "Virus–host association scoring" = "Virus-host\nassociation scoring",
  "Reservoir or vector prediction" = "Reservoir or\nvector\nprediction",
  "Human-infectivity prediction" = "Human-\ninfectivity\nprediction",
  "Host-adaptation scoring" = "Host-\nadaptation\nscoring",
  "Spillover-risk prioritization" = "Spillover-\nrisk\nprioritization"
)
tool_display <- c(
  "Host Taxon Predictor" = "HTP",
  "ViralHostPredictor" = "ViralHost\nPredictor",
  "Zoonotic rank model" = "zoonotic\nrank"
)
evidence_unit_code <- c(
  "DeepHoF" = "N",
  "RNAVirHost" = "N",
  "Host Taxon Predictor" = "N",
  "VPF-Class" = "V",
  "MENB" = "N",
  "UniVH" = "H",
  "EvoMIL" = "H",
  "VIDHOP" = "N",
  "HostNet" = "N",
  "MosViR" = "N",
  "ViralHostPredictor" = "N",
  "DeePaC-vir" = "S",
  "VirHostPRED" = "P",
  "Zoonotic rank model" = "S",
  "GIVAL" = "P",
  "SPHAK" = "P"
)
evidence_unit_labels <- c(
  "N" = "nucleotide sequence / genome / contig",
  "S" = "source species or taxon metadata",
  "H" = "virus-host pair / association",
  "P" = "protein record / accession",
  "V" = "VPF profile"
)

make_rounded_legend_graphics <- function(colors, fill_alpha, border_alpha,
                                         line_width = 0.7,
                                         radius = unit(1.1, "mm")) {
  lapply(
    colors,
    function(color_value) {
      force(color_value)
      function(x, y, w, h) {
        grid.roundrect(
          x = x,
          y = y,
          width = w * 0.88,
          height = h * 0.78,
          r = radius,
          gp = gpar(
            fill = adjustcolor(color_value, alpha.f = fill_alpha),
            col = adjustcolor(color_value, alpha.f = border_alpha),
            lwd = line_width
          )
        )
      }
    }
  )
}

make_tools_bar_legend_graphics <- function(values, colors, max_value,
                                           fill_alpha = 0.95,
                                           background_alpha = 0.28,
                                           radius = unit(1.1, "mm")) {
  lapply(
    seq_along(values),
    function(index) {
      value <- values[index]
      color_value <- colors[index]
      force(value)
      force(color_value)
      function(x, y, w, h) {
        full_width <- w * 0.90
        bar_width <- full_width * value / max_value
        left_edge <- x - full_width / 2
        grid.roundrect(
          x = x,
          y = y,
          width = full_width,
          height = h * 0.55,
          r = radius,
          gp = gpar(
            fill = adjustcolor("#D5DCE6", alpha.f = background_alpha),
            col = NA
          )
        )
        grid.roundrect(
          x = left_edge + bar_width / 2,
          y = y,
          width = bar_width,
          height = h * 0.55,
          r = radius,
          gp = gpar(
            fill = adjustcolor(color_value, alpha.f = fill_alpha),
            col = NA
          )
        )
      }
    }
  )
}

make_evidence_unit_badge_graphics <- function(codes,
                                              radius = unit(1.15, "mm")) {
  lapply(
    codes,
    function(code) {
      force(code)
      function(x, y, w, h) {
        grid.roundrect(
          x = x,
          y = y,
          width = h * 0.92,
          height = h * 0.82,
          r = radius,
          gp = gpar(
            fill = "#FFFFFF",
            col = "#000000",
            lwd = 1.2
          )
        )
        grid.text(
          code,
          x = x,
          y = y,
          gp = gpar(
            fontsize = 12.0,
            fontface = "bold",
            col = "#000000"
          )
        )
      }
    }
  )
}

read_project_csv <- function(path) {
  if (!file.exists(path)) {
    stop(sprintf("Required input is missing: %s", path), call. = FALSE)
  }
  read.csv(
    path,
    check.names = FALSE,
    stringsAsFactors = FALSE,
    fileEncoding = "UTF-8-BOM"
  )
}

display_tool <- function(tool) {
  replacement <- unname(tool_display[tool])
  ifelse(is.na(replacement), tool, replacement)
}

format_count <- function(value) {
  format(value, big.mark = ",", scientific = FALSE, trim = TRUE)
}

genome_class <- function(genome) {
  result <- rep(NA_character_, length(genome))
  result[grepl("-RT", genome, fixed = TRUE)] <- "reverse-transcribing"
  result[is.na(result) & grepl("dsDNA", genome, fixed = TRUE)] <- "dsDNA"
  result[is.na(result) & grepl("ssDNA", genome, fixed = TRUE)] <- "ssDNA"
  result[is.na(result) & grepl("dsRNA", genome, fixed = TRUE)] <- "dsRNA"
  result[
    is.na(result) &
      (grepl("ssRNA(-)", genome, fixed = TRUE) |
       grepl("ssRNA(+/-)", genome, fixed = TRUE))
  ] <- "(−)ssRNA"
  result[
    is.na(result) & grepl("ssRNA(+)", genome, fixed = TRUE)
  ] <- "(+)ssRNA"
  result
}

order_genome_class <- function(order_name, ictv_reference) {
  members <- ictv_reference[ictv_reference$Order == order_name, , drop = FALSE]
  member_classes <- genome_class(members$Genome)
  weights <- suppressWarnings(as.numeric(members$Species_count))
  weights[is.na(weights) | weights < 1] <- 1
  scores <- setNames(rep(0, length(genome_classes)), genome_classes)
  for (class_name in genome_classes) {
    scores[class_name] <- sum(weights[member_classes == class_name], na.rm = TRUE)
  }
  if (max(scores) == 0) {
    stop(sprintf("Cannot assign genome class to ICTV order: %s", order_name),
         call. = FALSE)
  }
  names(scores)[which.max(scores)]
}

order_genome_classes_present <- function(order_name, ictv_reference) {
  members <- ictv_reference[ictv_reference$Order == order_name, , drop = FALSE]
  member_classes <- unique(genome_class(members$Genome))
  member_classes <- member_classes[!is.na(member_classes)]
  genome_classes[genome_classes %in% member_classes]
}

make_order_labels <- function(order_names, ictv_reference, show_mixed_labels) {
  if (!show_mixed_labels) {
    return(order_names)
  }
  vapply(
    order_names,
    function(order_name) {
      classes_present <- order_genome_classes_present(order_name, ictv_reference)
      if (length(classes_present) <= 1L) {
        return(order_name)
      }
      paste0(
        order_name,
        " (mixed: ",
        paste(unname(genome_class_titles[classes_present]), collapse = "; "),
        ")"
      )
    },
    character(1)
  )
}

make_mixed_order_label_annotation <- function(order_names, majority_classes,
                                             classes_present,
                                             fontsize = 12.3,
                                             width = unit(82, "mm")) {
  AnnotationFunction(
    which = "row",
    n = length(order_names),
    width = width,
    show_name = FALSE,
    fun = function(index, k = NULL, N = NULL, vp_name = NULL) {
      n <- length(index)
      for (position in seq_along(index)) {
        source_index <- index[position]
        order_name <- order_names[source_index]
        majority_class <- as.character(majority_classes[source_index])
        present <- classes_present[[source_index]]
        y_position <- unit(1 - (position - 0.5) / n, "npc")

        if (length(present) <= 1L) {
          grid.text(
            order_name,
            x = unit(1, "npc"),
            y = y_position,
            just = c("right", "center"),
            gp = gpar(
              fontsize = fontsize,
              fontface = "bold",
              col = unname(genome_colors[majority_class])
            )
          )
          next
        }

        pieces <- list(
          list(text = paste0(order_name, " (mixed: "),
               color = unname(genome_colors[majority_class]))
        )
        for (class_index in seq_along(present)) {
          class_name <- present[class_index]
          pieces[[length(pieces) + 1L]] <- list(
            text = unname(genome_class_titles[class_name]),
            color = unname(genome_colors[class_name])
          )
          if (class_index < length(present)) {
            pieces[[length(pieces) + 1L]] <- list(
              text = "; ",
              color = "#000000"
            )
          }
        }
        pieces[[length(pieces) + 1L]] <- list(text = ")", color = "#000000")

        piece_widths <- lapply(
          pieces,
          function(piece) {
            grobWidth(textGrob(
              piece$text,
              gp = gpar(fontsize = fontsize, fontface = "bold")
            ))
          }
        )
        total_width <- Reduce(`+`, piece_widths)
        x_position <- unit(1, "npc") - total_width
        for (piece_index in seq_along(pieces)) {
          if (piece_index > 1L) {
            x_position <- x_position + piece_widths[[piece_index - 1L]]
          }
          grid.text(
            pieces[[piece_index]]$text,
            x = x_position,
            y = y_position,
            just = c("left", "center"),
            gp = gpar(
              fontsize = fontsize,
              fontface = "bold",
              col = pieces[[piece_index]]$color
            )
          )
        }
      }
    }
  )
}

load_figure_data <- function() {
  family_presence <- read_project_csv(family_presence_path)
  tool_metadata <- read_project_csv(tool_metadata_path)
  ictv_reference <- read_project_csv(ictv_reference_path)

  tool_metadata <- tool_metadata[!tool_metadata$Tool %in% excluded_tools, , drop = FALSE]
  if (length(unique(tool_metadata$Tool)) < 1L) {
    stop("Tool metadata must contain at least one plotted tool", call. = FALSE)
  }
  missing_tools <- setdiff(tool_metadata$Tool, family_presence$Tool)
  if (length(missing_tools) > 0L) {
    stop(
      sprintf("Tools configured but absent from scoped family-presence table: %s",
              paste(missing_tools, collapse = ", ")),
      call. = FALSE
    )
  }

  endpoint_levels <- unique(tool_metadata$Endpoint_category)
  tool_metadata$Endpoint_category <- factor(
    tool_metadata$Endpoint_category,
    levels = endpoint_levels
  )
  tool_metadata <- tool_metadata[
    order(tool_metadata$Endpoint_category, tool_metadata$Tool),
    ,
    drop = FALSE
  ]

  positive_observations <- family_presence[
    family_presence$Tool %in% tool_metadata$Tool,
    c("Tool", "Current_ICTV_family", "Order"),
    drop = FALSE
  ]
  positive_observations <- unique(positive_observations)

  family_total_lookup <- setNames(
    rep(0, length(tool_metadata$Tool)),
    tool_metadata$Tool
  )
  family_totals <- table(positive_observations$Tool)
  family_total_lookup[names(family_totals)] <- as.integer(family_totals)

  tool_order <- unlist(lapply(endpoint_levels, function(endpoint_name) {
    tools <- tool_metadata$Tool[
      tool_metadata$Endpoint_category == endpoint_name
    ]
    tools[order(-family_total_lookup[tools], tools)]
  }), use.names = FALSE)
  tool_metadata <- tool_metadata[
    match(tool_order, tool_metadata$Tool),
    ,
    drop = FALSE
  ]
  positive_observations$Order[
    is.na(positive_observations$Order)
  ] <- ""
  family_reference_eukaryotic <- ictv_reference[
    ictv_reference$Current_ICTV_family %in%
      unique(positive_observations$Current_ICTV_family),
    ,
    drop = FALSE
  ]

  assigned_observations <- positive_observations[
    positive_observations$Order != "",
    ,
    drop = FALSE
  ]
  assigned_observations <- unique(assigned_observations)
  orders <- unique(assigned_observations$Order)
  order_classes <- vapply(
    orders,
    order_genome_class,
    character(1),
    ictv_reference = family_reference_eukaryotic
  )
  orders <- orders[order(match(order_classes, genome_classes), orders)]
  order_classes <- order_classes[orders]

  coverage <- matrix(
    0,
    nrow = length(orders),
    ncol = length(tool_order),
    dimnames = list(orders, tool_order)
  )
  if (nrow(assigned_observations) > 0L) {
    order_totals <- aggregate(
      Current_ICTV_family ~ Tool + Order,
      data = assigned_observations,
      FUN = length
    )
    for (row_index in seq_len(nrow(order_totals))) {
      coverage[
        order_totals$Order[row_index],
        order_totals$Tool[row_index]
      ] <- order_totals$Current_ICTV_family[row_index]
    }
  }
  rownames(coverage) <- orders

  unassigned <- setNames(rep(0, length(tool_order)), tool_order)
  unassigned_observations <- positive_observations[
    positive_observations$Order == "",
    ,
    drop = FALSE
  ]
  if (nrow(unassigned_observations) > 0L) {
    unassigned_totals <- table(unassigned_observations$Tool)
    unassigned[names(unassigned_totals)] <- as.integer(unassigned_totals)
  }

  tools_per_class <- setNames(rep(0, length(genome_classes)), genome_classes)
  for (class_name in genome_classes) {
    class_orders <- orders[order_classes == class_name]
    if (length(class_orders) > 0L) {
      tools_per_class[class_name] <- sum(
        colSums(coverage[class_orders, , drop = FALSE] > 0) > 0
      )
    }
  }

  list(
    coverage = coverage,
    tools = tool_order,
    endpoint = factor(
      as.character(tool_metadata$Endpoint_category),
      levels = endpoint_levels
    ),
    endpoint_levels = endpoint_levels,
    order_classes = factor(order_classes, levels = genome_classes),
    order_counts = colSums(coverage > 0),
    family_counts = as.numeric(family_total_lookup[tool_order]),
    unassigned = as.numeric(unassigned[tool_order]),
    tools_per_order = rowSums(coverage > 0),
    tools_per_class = tools_per_class,
    order_labels_plain = make_order_labels(
      rownames(coverage),
      family_reference_eukaryotic,
      show_mixed_labels = FALSE
    ),
    order_labels_mixed = make_order_labels(
      rownames(coverage),
      family_reference_eukaryotic,
      show_mixed_labels = TRUE
    ),
    order_classes_present = lapply(
      rownames(coverage),
      order_genome_classes_present,
      ictv_reference = family_reference_eukaryotic
    )
  )
}

make_text_annotation <- function(labels, fontsize = 9.0, colors = "#082F49",
                                 height = unit(4.2, "mm"), show_name = TRUE,
                                 rotation = 0, location = 0.5,
                                 justification = "center",
                                 background_fill = NULL) {
  gp_args <- list(
    fontsize = fontsize,
    fontface = "bold",
    col = colors
  )
  if (!is.null(background_fill)) {
    gp_args$fill <- background_fill
  }
  anno_text(
    labels,
    gp = do.call(gpar, gp_args),
    rot = rotation,
    location = location,
    just = justification,
    height = height,
    show_name = show_name
  )
}

make_tool_label_annotation <- function(labels, endpoint, fontsize = 10.0,
                                       height = unit(38, "mm")) {
  label_fill <- adjustcolor(
    unname(endpoint_colors[as.character(endpoint)]),
    alpha.f = 0.22
  )
  AnnotationFunction(
    which = "column",
    n = length(labels),
    height = height,
    show_name = FALSE,
    fun = function(index, k = NULL, N = NULL, vp_name = NULL) {
      n <- length(index)
      endpoint_values <- as.character(endpoint[index])
      run_starts <- c(1, which(endpoint_values[-1] != endpoint_values[-n]) + 1)
      run_ends <- c(run_starts[-1] - 1, n)
      for (run_index in seq_along(run_starts)) {
        start <- run_starts[run_index]
        end <- run_ends[run_index]
        endpoint_name <- endpoint_values[start]
        endpoint_color <- unname(endpoint_colors[endpoint_name])
        grid.roundrect(
          x = (start + end - 1) / (2 * n),
          y = 0.5,
          width = (end - start + 1) / n,
          height = 0.96,
          r = unit(1.8, "mm"),
          gp = gpar(
            fill = adjustcolor(endpoint_color, alpha.f = 0.22),
            col = adjustcolor(endpoint_color, alpha.f = 0.38),
            lwd = 0.55
          )
        )
      }
      for (position in seq_along(index)) {
        source_index <- index[position]
        unit_code <- unname(evidence_unit_code[labels[source_index]])
        if (!is.na(unit_code) && nzchar(unit_code)) {
          grid.roundrect(
            x = (position - 0.5) / n,
            y = unit(0.925, "npc"),
            width = unit(4.9, "mm"),
            height = unit(4.9, "mm"),
            r = unit(1.15, "mm"),
            gp = gpar(
              fill = "#FFFFFF",
              col = "#000000",
              lwd = 1.05
            )
          )
          grid.text(
            unit_code,
            x = (position - 0.5) / n,
            y = unit(0.925, "npc"),
            gp = gpar(
              fontsize = 10.7,
              fontface = "bold",
              col = "#000000"
            )
          )
        }
        grid.text(
          labels[source_index],
          x = (position - 0.5) / n,
          y = unit(0.025, "npc"),
          rot = 90,
          just = "left",
          gp = gpar(
            fontsize = fontsize,
            fontface = "bold",
            col = "#000000"
          )
        )
      }
    }
  )
}

make_rounded_tools_per_order_annotation <- function(values, fill_colors,
                                                    max_value,
                                                    width = unit(34, "mm")) {
  AnnotationFunction(
    which = "row",
    n = length(values),
    width = width,
    show_name = TRUE,
    fun = function(index, k = NULL, N = NULL, vp_name = NULL) {
      n <- length(index)
      bar_area_width <- 0.78
      for (position in seq_along(index)) {
        source_index <- index[position]
        value <- values[source_index]
        y_position <- 1 - (position - 0.5) / n
        bar_width <- bar_area_width * value / max_value
        grid.roundrect(
          x = unit(bar_width / 2, "npc"),
          y = unit(y_position, "npc"),
          width = unit(bar_width, "npc"),
          height = unit(0.64 / n, "npc"),
          r = unit(1.2, "mm"),
          just = c("center", "center"),
          gp = gpar(
            fill = fill_colors[source_index],
            col = NA
          )
        )
        grid.text(
          value,
          x = unit(bar_width + 0.035, "npc"),
          y = unit(y_position, "npc"),
          just = c("left", "center"),
          gp = gpar(
            fontsize = 13.4,
            fontface = "bold",
            col = "#082F49"
          )
        )
      }
    }
  )
}

build_heatmap <- function(data, show_mixed_order_labels = FALSE,
                          column_cell_width_mm = 10.9,
                          filled_cell_alpha = 0.23,
                          filled_cell_text_color = "#000000") {
  coverage <- data$coverage
  n_tools <- length(data$tools)
  order_labels <- if (show_mixed_order_labels) {
    data$order_labels_mixed
  } else {
    data$order_labels_plain
  }
  top_annotation <- HeatmapAnnotation(
    `Tool labels` = make_tool_label_annotation(
      data$tools,
      data$endpoint,
      fontsize = 14.8,
      height = unit(62, "mm")
    ),
    gp = gpar(col = NA),
    show_legend = FALSE,
    show_annotation_name = FALSE,
    annotation_name_side = "left",
    annotation_name_rot = 0,
    annotation_name_gp = gpar(
      fontsize = 14.2,
      fontface = "bold",
      col = "#0B4F6C"
    ),
    gap = unit(0, "mm")
  )

  bottom_annotation <- HeatmapAnnotation(
    Orders = make_text_annotation(
      data$order_counts,
      fontsize = 14.2,
      height = unit(5.0, "mm")
    ),
    Families = make_text_annotation(
      data$family_counts,
      fontsize = 14.2,
      height = unit(5.0, "mm")
    ),
    `Families without order assignment, n` = make_text_annotation(
      data$unassigned,
      fontsize = 13.4,
      colors = ifelse(data$unassigned > 0, "#0B4F6C", "#6E9BC7"),
      height = unit(5.5, "mm")
    ),
    annotation_name_side = "left",
    annotation_name_rot = 0,
    annotation_name_gp = gpar(
      fontsize = 13.2,
      fontface = "bold",
      col = "#0B4F6C"
    ),
    gap = unit(0.5, "mm")
  )

  right_annotation <- rowAnnotation(
    `Right spacer` = anno_empty(
      width = unit(3.0, "mm"),
      border = FALSE,
      show_name = FALSE
    ),
    `Tools covering\nthe order, n` = make_rounded_tools_per_order_annotation(
      values = data$tools_per_order,
      fill_colors = unname(genome_colors[as.character(data$order_classes)]),
      max_value = n_tools,
      width = unit(34, "mm")
    ),
    annotation_name_side = "top",
    annotation_name_rot = 0,
    annotation_name_gp = gpar(
      fontsize = 14.2,
      fontface = "bold",
      col = "#082F49"
    )
  )

  class_slices <- levels(droplevels(data$order_classes))
  class_slice_labels <- unname(genome_class_titles[class_slices])
  genome_class_block <- anno_block(
      which = "row",
      gp = gpar(
        fill = rep(NA_character_, length(class_slices)),
        col = unname(genome_colors[class_slices]),
        lwd = 1.35
      ),
      labels = class_slice_labels,
      labels_gp = gpar(
        fontsize = 12.8,
        fontface = "bold",
        col = unname(genome_colors[class_slices])
      ),
      labels_rot = 90
  )

  if (show_mixed_order_labels) {
    genome_class_annotation <- rowAnnotation(
      `Order labels` = make_mixed_order_label_annotation(
        rownames(coverage),
        data$order_classes,
        data$order_classes_present,
        fontsize = 13.4,
        width = unit(90, "mm")
      ),
      `Genome class` = genome_class_block,
      annotation_width = unit(c(90, 9.0), "mm"),
      gap = unit(1.5, "mm"),
      show_annotation_name = FALSE
    )
  } else {
    genome_class_annotation <- rowAnnotation(
      `Genome class` = genome_class_block,
      width = unit(9.0, "mm"),
      show_annotation_name = FALSE
    )
  }

  matrix_heatmap <- Heatmap(
    coverage,
    name = "family_count",
    width = unit(ncol(coverage) * column_cell_width_mm, "mm"),
    col = c("0" = "#FFFFFF", "1" = "#FFFFFF"),
    rect_gp = gpar(type = "none"),
    cluster_rows = FALSE,
    cluster_columns = FALSE,
    cluster_row_slices = FALSE,
    cluster_column_slices = FALSE,
    column_split = data$endpoint,
    column_title = NULL,
    column_title_gp = gpar(fontsize = 0),
    column_gap = unit(2.4, "mm"),
    row_split = data$order_classes,
    row_title = NULL,
    row_gap = unit(0.20, "mm"),
    column_order = seq_len(ncol(coverage)),
    show_row_names = !show_mixed_order_labels,
    row_names_side = "left",
    row_names_gp = gpar(
      fontsize = 13.4,
      fontface = "bold",
      col = unname(genome_colors[as.character(data$order_classes)])
    ),
    row_labels = order_labels,
    row_names_max_width = if (show_mixed_order_labels) {
      unit(78, "mm")
    } else {
      unit(40, "mm")
    },
    show_column_names = FALSE,
    show_heatmap_legend = FALSE,
    top_annotation = top_annotation,
    bottom_annotation = bottom_annotation,
    left_annotation = genome_class_annotation,
    right_annotation = right_annotation,
    cell_fun = function(j, i, x, y, width, height, fill) {
      value <- coverage[i, j]
      if (is.na(value) || value <= 0) {
        grid.roundrect(
          x,
          y,
          width * 0.82,
          height * 0.70,
          r = unit(1.2, "mm"),
          gp = gpar(
            fill = adjustcolor("#BFC8D4", alpha.f = 0.34),
            col = NA
          )
        )
      } else {
        cell_color <- unname(genome_colors[as.character(data$order_classes[i])])
        grid.roundrect(
          x,
          y,
          width * 0.88,
          height * 0.78,
          r = unit(1.4, "mm"),
          gp = gpar(
            fill = adjustcolor(cell_color, alpha.f = filled_cell_alpha),
            col = adjustcolor(cell_color, alpha.f = 0.95),
            lwd = 0.65
          )
        )
        grid.text(
          value,
          x,
          y,
          gp = gpar(
            col = filled_cell_text_color,
            fontsize = 13.4,
            fontface = "bold"
          )
        )
      }

    }
  )

  genome_class_legend <- Legend(
    title = "Genome class\ncell value = unique families",
    labels = genome_class_display,
    graphics = make_rounded_legend_graphics(
      unname(genome_colors),
      fill_alpha = filled_cell_alpha,
      border_alpha = 0.95,
      line_width = 1.15
    ),
    grid_width = unit(7.2, "mm"),
    grid_height = unit(5.2, "mm"),
    ncol = 1,
    direction = "vertical",
    title_position = "topleft",
    labels_gp = gpar(fontsize = 15.4, col = "#000000"),
    title_gp = gpar(fontsize = 16.2, fontface = "bold", col = "#000000"),
    gap = unit(0.7, "mm")
  )
  genome_tools_legend <- Legend(
    title = "Tools, n\n ",
    labels = as.character(data$tools_per_class[genome_classes]),
    graphics = make_tools_bar_legend_graphics(
      values = data$tools_per_class[genome_classes],
      colors = unname(genome_colors),
      max_value = length(data$tools),
      fill_alpha = 0.95
    ),
    grid_width = unit(16.0, "mm"),
    grid_height = unit(5.2, "mm"),
    ncol = 1,
    direction = "vertical",
    title_position = "topleft",
    labels_gp = gpar(fontsize = 15.4, col = "#000000", fontface = "bold"),
    title_gp = gpar(fontsize = 16.2, fontface = "bold", col = "#000000"),
    gap = unit(0.7, "mm")
  )
  genome_legend <- packLegend(
    genome_class_legend,
    genome_tools_legend,
    direction = "horizontal",
    gap = unit(5.0, "mm")
  )
  endpoint_legend <- Legend(
    title = "Prediction endpoint",
    labels = as.character(data$endpoint_levels),
    graphics = make_rounded_legend_graphics(
      unname(endpoint_colors[as.character(data$endpoint_levels)]),
      fill_alpha = 0.22,
      border_alpha = 0.85,
      line_width = 1.05,
      radius = unit(1.4, "mm")
    ),
    grid_width = unit(7.2, "mm"),
    grid_height = unit(5.2, "mm"),
    ncol = 1,
    direction = "vertical",
    title_position = "topleft",
    labels_gp = gpar(fontsize = 15.2, col = "#000000"),
    title_gp = gpar(fontsize = 16.8, fontface = "bold", col = "#000000"),
    gap = unit(0.7, "mm")
  )
  evidence_unit_legend <- Legend(
    title = "Evidence unit",
    labels = unname(evidence_unit_labels),
    graphics = make_evidence_unit_badge_graphics(names(evidence_unit_labels)),
    grid_width = unit(6.4, "mm"),
    grid_height = unit(5.2, "mm"),
    ncol = 1,
    direction = "vertical",
    title_position = "topleft",
    labels_gp = gpar(fontsize = 14.5, col = "#000000"),
    title_gp = gpar(fontsize = 16.8, fontface = "bold", col = "#000000"),
    gap = unit(0.7, "mm")
  )

  list(
    heatmap = matrix_heatmap,
    legends = packLegend(
      genome_legend,
      endpoint_legend,
      evidence_unit_legend,
      direction = "vertical",
      gap = unit(7.0, "mm")
    )
  )
}

draw_figure <- function(figure_objects) {
  grid.newpage()
  draw(
    figure_objects$heatmap,
    newpage = FALSE,
    merge_legends = TRUE,
    heatmap_legend_list = list(figure_objects$legends),
    heatmap_legend_side = "right",
    annotation_legend_side = "right",
    align_heatmap_legend = "global_center",
    row_title = "ICTV 2026 orders",
    row_title_side = "left",
    row_title_gp = gpar(
      fontsize = 14.4,
      fontface = "bold",
      col = "#0B4F6C"
    ),
    column_title = NULL,
    column_title_gp = gpar(
      fontsize = 16,
      fontface = "bold",
      col = "#061F3C"
    ),
    padding = unit(c(5.0, 1.5, 1.5, 1.5), "mm")
  )
}

render_output_set <- function(data, stem, show_mixed_order_labels,
                              width = 12.2, height = 16.2,
                              column_cell_width_mm = 10.9,
                              filled_cell_alpha = 0.23,
                              filled_cell_text_color = "#000000") {
  figure_objects <- build_heatmap(
    data,
    show_mixed_order_labels = show_mixed_order_labels,
    column_cell_width_mm = column_cell_width_mm,
    filled_cell_alpha = filled_cell_alpha,
    filled_cell_text_color = filled_cell_text_color
  )
  outputs <- c(
    png = paste0(stem, ".png"),
    pdf = paste0(stem, ".pdf"),
    svg = paste0(stem, ".svg"),
    tiff = paste0(stem, ".tiff"),
    preview = paste0(stem, "_preview.png")
  )

  png(outputs[["png"]], width = width, height = height, units = "in",
      res = 300, type = "cairo", bg = "white")
  draw_figure(figure_objects)
  dev.off()

  cairo_pdf(outputs[["pdf"]], width = width, height = height,
            onefile = TRUE, bg = "white")
  draw_figure(figure_objects)
  dev.off()

  svg(outputs[["svg"]], width = width, height = height,
      onefile = TRUE, bg = "white")
  draw_figure(figure_objects)
  dev.off()

  tiff(outputs[["tiff"]], width = width, height = height, units = "in",
       res = 300, compression = "lzw", type = "cairo", bg = "white")
  draw_figure(figure_objects)
  dev.off()

  png(outputs[["preview"]], width = width, height = height, units = "in",
      res = 140, type = "cairo", bg = "white")
  draw_figure(figure_objects)
  dev.off()

  unname(outputs)
}

render_outputs <- function() {
  dir.create(main_figures_dir, recursive = TRUE, showWarnings = FALSE)
  data <- load_figure_data()
  c(
    render_output_set(
      data,
      file.path(main_figures_dir, "vertical_taxonomic_coverage_scope_corrected"),
      show_mixed_order_labels = TRUE,
      width = 22.34,
      height = 18.0,
      column_cell_width_mm = 11.8
    )
  )
}

if (!identical(Sys.getenv("VIRAL_HEATMAP_LIBRARY_ONLY"), "1")) {
  outputs <- render_outputs()
  for (path in outputs) {
    cat(sub(paste0("^", package_root, "/"), "", path), "\n", sep = "")
  }
}
