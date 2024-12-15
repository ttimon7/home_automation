# LED Controller


## Docker build

1. Enabling extended build capabilities

   ```
   docker buildx install
   docker buildx create --use
   ```

2. Building the image

   `sudo docker buildx build . --platform linux/arm/v8 -t $HOST:$PORT/soothworks/led-controller:armv8 --load`

3. Start a private registry

   `sudo docker run -it -p $PORT:5000 --rm --name registry registry:2.8`

4. Make it as as an insecure registry if needed (on both host and target machine)

   `sudo printf "{\n/etc/docker/daemon.json\n}\n" > /etc/docker/daemon.json`

   ([source](https://stackoverflow.com/questions/49674004/docker-repository-server-gave-http-response-to-https-client))

5. Restart Docker

   `sudo systemctl restart docker.service`

6. Push image to registry

   `sudo docker push $HOST:$PORT/soothworks/led-controller:armv8`

7. Pull image on target machine:

   `sudo docker run -it --rm $HOST:$PORT/soothworks/led-controller:armv8`


This works:

ttimon7@ruby:~/work $ sudo docker run -it --rm --privileged --network=host 192.168.0.80:5000/soothworks/led-controller:armv8 bash
root@9efaea6700e6:/app# hypercorn -w1 --reload -b0.0.0.0:$PORT sootworks.led_controller.app:app