# MKM Inventory Tool

## Overview
I created this tool for myself to keep track of sealed mtg products i bought. It queues the MKM V2 API to fetch current prices for a given inventory file (and configured countries). The formatted output is printed as Pretty Table (ASCII) to stdout. 

This is a sample output showing prices for three regions (Austria, Germany, International):

![Sample Outpu](/doc/MKM_Inventory_Tool_Example.png?raw=true "")

## Requirements
* requests_oauthlib
* PTable
* json
* ruamel.yaml
* colorama

`pip install -r requirements.txt`

## Prerequisite

* Add your MKM access secrets and tokens to config.yaml (You can find them when logged into your cardmarket account: Accountname -> Account -> API Settings)
* Configure the desired countries to fetch the prices from in config.yaml
* Remove sample stock and add your stock to inventory.yaml
  * You'll need to enter the MKM product id for every product you want to track. An easy way to locate the product id is to look at the product picture at the MKM Website. The filename represents the product id.

## Usage

`python3 mkm_inventory_tool.py`

or run mkm_inventory_tool.exe

## Disclaimer

This is a very basic tool that has been created in a few hours of my spare time to get some work done. No polishing or optimizing has been done yet, so use at your own risk.
