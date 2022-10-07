docker build -t testimage . || exit 1
docker run -it  -p9001:80 testimage
