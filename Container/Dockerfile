FROM centos:centos8
 
RUN yum -y update; yum clean all
RUN yum -y install net-tools iproute unzip git
RUN yum -y install openssh-server openssh-clients

RUN ssh-keygen -f /etc/ssh/ssh_host_rsa_key -N '' -t rsa
RUN ssh-keygen -f /etc/ssh/ssh_host_ed25519_key -N '' -t ed25519
RUN ssh-keygen -f /etc/ssh/ssh_host_ecdsa_key -N '' -t ecdsa

RUN yum -y install wget tar maven gcc-c++
RUN yum -y install java-1.8.0-openjdk


RUN mkdir -p /root/.ssh
COPY ./authorized_keys /root/.ssh/

COPY ./start_container.sh /root/

EXPOSE 22
ENTRYPOINT ["/root/start_container.sh"]
