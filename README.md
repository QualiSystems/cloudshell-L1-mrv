# cloudshell-L1-mrv
[![Build status](https://travis-ci.org/QualiSystems/cloudshell-L1-mrv.svg?branch=dev)](https://travis-ci.org/QualiSystems/cloudshell-L1-mrv)
[![Coverage Status](https://coveralls.io/repos/github/QualiSystems/cloudshell-L1-mrv/badge.svg?branch=dev)](https://coveralls.io/github/QualiSystems/cloudshell-L1-mrv?branch=dev)
[![Dependency Status](https://dependencyci.com/github/QualiSystems/cloudshell-L1-mrv/badge)](https://dependencyci.com/github/QualiSystems/cloudshell-L1-mrv)
[![Stories in Ready](https://badge.waffle.io/QualiSystems/cloudshell-L1-mrv.svg?label=ready&title=Ready)](http://waffle.io/QualiSystems/cloudshell-L1-mrv)

<p align="center">
<img src="https://github.com/QualiSystems/devguide_source/raw/master/logo.png"></img>
</p>

# MRV MCC GENERIC L1 DRIVER

# Overview
The MRV MCC GENERIC Driver provides TestShell Resource Manager with the capability to communicate with MRV switches that are part of the Resource Manager inventory.
End users will be able to create routes, configure port settings, and read values from the switch using a Resource Manager client, or the TestShell API.

# Commands
| Feature | Description |
| --- | --- |
| MapBidi | Creates a bidir connection between two ports. |
| MapUni  | Creates a unidir connection between two ports. |
| MapClear | Clears any connection ending in this port. |
| MapClearTo | Clears a unidir connection between two ports. |
| MapTap | Creates a unidir connection between two ports. |
| GetAttribute | Return the value of a specific resource’s attribute. |
| SetAttribute | Sets the value of a specific resource’s attribute. |
