Creating container that provides a 'VM' in which to experiment with the tools.

1. Place a public keys for ssh into file 'authorized_keys' in the 'Container' directory

2. docker build -t centos8_plain:v1 .

3. docker run --init -d centos8_plain:v1 .

4. docker ps -a
   docker logs <containerid>

   The log contains the network config of the container,
   from which the ip address can be extracted.

   An alternative is to 'inspect' the container.

5. ssh root@<container-ip-address>

   If the host from which the ssh is initiated has proper access to
   the docker network and the private key matching one of the
   public keys deposited into the container, this allows
   access similar to a real system/VM.
   If the container has internet access, 'yum install ...' and
   'git clone ...' inside the container work as well to
   expand functionality.
   