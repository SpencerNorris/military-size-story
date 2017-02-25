#Generates sunburst graph of military equipment for the top five best-funded
#militaries in the world (USA, Russia, China, Saudi Arabia and the UK).
#Copied directly from http://stackoverflow.com/questions/12926779/how-to-make-a-sunburst-plot-in-r-or-python
library(sunburstR)
library(htmlwidgets)
library(shiny)

sequences <- read.csv(
   "../data/military-equipment-2015-top-five-aircraft-sequences.csv"
  ,header=F
  ,stringsAsFactors = FALSE)


sunburstOutput <- function(outputId, width = "100%", height = "700px") {
  shinyWidgetOutput(outputId, "sunburst", width, height, package = "sunburstR")
}
#' @export
renderSunburst <- function(expr, env = parent.frame(), quoted = FALSE) {
  if (!quoted) { expr <- substitute(expr) } # force quoted
  shinyRenderWidget(expr, sunburstOutput, env, quoted = TRUE)
}

ui = shinyUI(fluidPage(sunburstOutput('sunburst')))

server = function(input, output) {
  output$sunburst <- renderSunburst(sunburst(sequences))
}

shinyApp(ui = ui, server = server)