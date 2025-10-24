#!/bin/bash
hypercorn app.main:app --bind 0.0.0.0:8000

