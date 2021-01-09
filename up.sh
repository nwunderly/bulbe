git pull
docker build . --tag bulbe:latest

#docker run -d \
# --name bulbe_main \
# --network prod \
# -v $PWD/logs/bulbe:/bulbe/logs \
# --restart unless-stopped \
# bulbe discord

docker run -d \
 --name bulbe_github \
 --network prod \
 -v $PWD/logs/github:/logs \
 -v $PWD/data:/data \
 --restart unless-stopped \
 bulbe github --dev --debug