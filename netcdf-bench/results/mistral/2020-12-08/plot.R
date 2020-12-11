#!/usr/bin/env Rscript
cls=c(config="character", ppn="numeric", nodes="numeric", op="character", tp="numeric")
d = read.csv("data.csv", header=T, colClasses=cls, stringsAsFactors=FALSE, sep=" ")

library(ggplot2)
library(dplyr)

d$nodes = as.factor(d$nodes)
d$ppn = as.factor(d$ppn)
d$op = as.factor(d$op)
d$config = as.factor(d$config)
d$tp = d$tp / 1024

ggplot(d %>% filter(ppn==1 & op=="write"), aes(nodes, tp, color=config))  + geom_boxplot(position=position_dodge(1)) + ylab("Performance in GiB/s") + xlab("Nodes") + theme(legend.position="bottom")
ggsave("ppn1-write.pdf")

ggplot(d %>% filter(ppn==1 & op=="read"), aes(nodes, tp, color=config))  + geom_boxplot(position=position_dodge(1)) + ylab("Performance in GiB/s") + xlab("Nodes") + theme(legend.position="bottom")
ggsave("ppn1-read.pdf")

ggplot(d %>% filter(nodes==100 & op=="write"), aes(ppn, tp, color=config))  + geom_boxplot(position=position_dodge(1)) + ylab("Performance in GiB/s") + xlab("PPN") + theme(legend.position="bottom")
ggsave("nodes100-write.pdf")

ggplot(d %>% filter(nodes==100 & op=="read"), aes(ppn, tp, color=config))  + geom_boxplot(position=position_dodge(1)) + ylab("Performance in GiB/s") + xlab("PPN") + theme(legend.position="bottom")
ggsave("nodes100-read.pdf")
