---
title: CCW-001 "Bad Initialisation"
---

&emsp;Used when variable or data are initialised before being used, but are not initialised properly.

&emsp;For example: if you have an array of 1024 items to initialise, but due to faulty logic, only the first 1023 items are initialised, or if you initialise everything to zeros while the rest of the code expects ones.