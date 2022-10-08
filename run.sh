docker volume create boodschappen_data
docker build -t testimage . || exit 1

docker run \
    -it \
    -v $(pwd)/data:/data \
    -p9001:80 \
    testimage

#    testimage \
#    ls -ld /bdata
