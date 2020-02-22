#!/usr/bin/env bash

# Copy necessary dependencies from build

mkdir build &&
  cd build &&
  cmake3 .. &&
  cmake3 --build . --config Release &&
  make aws-lambda-package-tagger

printf "\n\n############### APP SIZE ###############\n\n"
du -sh /home/app/build/tagger
printf "\n\n################# END ##################\n\n"
