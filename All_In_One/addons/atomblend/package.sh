#!/bin/bash

cd ..
zip atomblend_public-$1.zip \
	atomblend_public/*.py \
	atomblend_public/atomtex.png \
	atomblend_public/analysis/* \
	atomblend_public/aptread/* \
	atomblend_public/blend/* \
	atomblend_public/docs/* \
	atomblend_public/templates/* \
	atomblend_public/README.md

