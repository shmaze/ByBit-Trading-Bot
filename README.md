# ByBit-Trading-Bot

This is a python script intended to intake predictions from an existing Machine Learning model and using those predictions to open trading positions 
on the trading platform ByBit.

The model is trained using available data from the python-binance library to make predictions, depending on the result of those predictions the script will open 
either a long or short position on the BTCUSD inverse perpetual contract on the ByBit testnet. 

This includes setting appropriate stop loss and take profit points.
Using this data we should be able to quantify the success of the predictor model. This script will be run once a day at noon GMT as a basis for consistency.

Will be updating with P/L as that information becomes available.
