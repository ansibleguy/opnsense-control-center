# Logserver

## MongoDB

Not starting with error:

```
WARNING: MongoDB 5.0+ requires a CPU with AVX support, and your current system does not appear to have that!
```

If you run the server as a VM - set its CPU-type to 'host'. (no generic virtual qemu type)

# Rebuild Docker Containers

Update target versions in docker-compose files (_/etc/opn-cc/docker-compose/*.yml_)

Stop the services.

```bash
systemctl stop opn-cc-*.service
```

Remove the containers and images.
```bash
docker ps -a
docker rm $CONTAINER_NAME

docker image ls
docker image rm $IMAGE_NAME
```

Clear build cache.

```bash
docker builder prune
```

Start services to re-build the containers.

```bash
systemctl start opn-cc-*.service
```
