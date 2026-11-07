library(tidyverse)
library(didimputation)
library(fixest)
library(did)

did_imputation_to_python <- function(df, coll){

  df[df$treatment == 0, "year_reclassified"] = 0

  static <- did_imputation(data = df, yname = coll, gname = "year_reclassified",
                           tname = "year", idname = "factorized")

  es <- did_imputation(data = df, yname = coll, gname = "year_reclassified",
                       tname = "year", idname = "factorized",
                       horizon=TRUE, pretrends = -2:-1)
  
  pts <- es %>%
    select(rel_year = term, estimate, std.error) %>%
    mutate(
      ci_lower = estimate - 1.96 * std.error,
      ci_upper = estimate + 1.96 * std.error,
      group = "DID Imputation Estimate",
      rel_year = as.numeric(rel_year)
    ) %>%
    filter(rel_year >= -20 & rel_year <= 30) %>%
    mutate(rel_year = rel_year + 0.1)
  
  # return(as.data.frame(static))
  
  return(list(as.data.frame(static), as.data.frame(pts)))
}
