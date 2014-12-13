

library(ggplot2)
library(reshape2)
library(stats)

plotsave <- function(filename = default_name(plot), plot = last_plot(),
                     width = 640, height = 480, res = NA, units = "px") {
  png(filename, width=width, height=height, res=res, units=units)
  print(plot)
  dev.off()
}

plotprint <- function(filename = default_name(plot), plot = last_plot(),
                      width = 4 * 1.3, height = 4, res = 300, units = "in") {
  plotsave(filename=filename, plot=plot, width=width, height=height, res=res, units=units)
}

theme_legend_rightdown <- function() {
  theme(legend.title=element_blank(), legend.position=c(1, 0), legend.justification=c(1, 0))
}

imp01 <- read.csv("tst_imp_01.csv")
imp02 <- read.csv("tst_imp_02.csv")
org01 <- read.csv("tst_org_01.csv")
org02 <- read.csv("tst_org_02.csv")

imp <- data.frame(method="Improved", rbind(imp01, imp02))
org <- data.frame(method="Original", rbind(org01, org02))

cc <- rbind(imp, org)
cc.st <- aggregate(diff ~ method + cert_num, data=cc, mean)
p <- ggplot(cc.st, aes(x=cert_num, y=diff, colour=method)) + geom_line() + geom_point() + 
  labs(x="Number of Tested Frankencerts", y="Average Discrepancy Count") +
  theme_linedraw() + theme_legend_rightdown()
plotprint("result_line.png")

p <- ggplot(cc, aes(x=factor(cert_num), y=diff, fill=method)) + geom_boxplot() +
  labs(x="Number of Tested Frankencerts", y="Discrepancy Count") +
  theme_linedraw() + theme_legend_rightdown()
plotprint("result_boxplot.png")

# cc.m <- melt(cc, id=c("method", "cert_num"))
# ggplot(cc.m, aes(x=cert_num, y=value, fill=variable)) + geom_boxplot()

