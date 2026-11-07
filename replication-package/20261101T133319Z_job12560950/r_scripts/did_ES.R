library(tidyverse)
library(didimputation)
library(fixest)
library(did)
event_study <- function(df, coll){
  fml <- as.formula(
    paste0(
      coll,
      " ~ i(eventyear, treated_final, ref = -1) ",
      " | factorized + year"
    )
  )
  model <- feols(fml, data = df, cluster = 'factorized')
  
  print(summary(model))
  return(c(as.data.frame(coef(model)), as.data.frame(se(model))))
}


DiD <- function(df, coll){
  fml <- as.formula(
    paste0(
      coll,
      " ~ posttreat",
      " | factorized + year"
    )
  )
  model <- feols(fml, data = df, cluster = 'factorized')
  
  print(summary(model))
  return(c(as.data.frame(coef(model)), as.data.frame(se(model))))
  
}

DiD_LR <- function(df, coll){
    fml <- as.formula(
      paste0(
        coll,
        " ~ posttreatLR",
        " | posttreatSR + factorized + year"
      )
    )
    model <- feols(fml, data = df, cluster = 'factorized')
    
    print(summary(model))
    return(c(as.data.frame(coef(model)), as.data.frame(se(model))))
}