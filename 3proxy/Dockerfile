FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y wget && \
    wget https://github.com/z3APA3A/3proxy/releases/download/0.9.4/3proxy-0.9.4.x86_64.deb && \
    dpkg -i 3proxy-0.9.4.x86_64.deb && \
    mkdir -p /etc/3proxy /var/log/3proxy && \
    rm 3proxy-0.9.4.x86_64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY 3proxy.cfg /etc/3proxy/3proxy.cfg
COPY passwd /etc/3proxy/passwd

RUN chmod 600 /etc/3proxy/passwd

EXPOSE 1080 3128

CMD ["/usr/bin/3proxy", "/etc/3proxy/3proxy.cfg"]