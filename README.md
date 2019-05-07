# Financial time series modeling and forecasting with deep neural networks

## Info

Author: Márton Torner

Supervisor: Bálint Gyires-Tóth, PhD

## Task

The task is to collect Limit Order Book data from a chosen cryptocurrency, to analyze and process the gathered records and to develop a neural network based solution to predict the direction of the price movement of the asset-pairs.

In this work, level 100 data (Limit Order Book, depth: 100) is used from Kraken crypto ex- change. The live order flow is queried with the help of the provided API and saved on local storage. The aim is to create a Deep Learning powered system which can predict the price movement di- rection from the given history with better results than the baseline solutions. The first approaches are models based on autoregressive solutions (logistic regression and random forest regression) and then I try to use a deep neural network as the model.

In the future, this work can be used as a base for creating a complex algorithmic trading system.