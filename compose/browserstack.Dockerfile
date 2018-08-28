FROM ubuntu:latest

RUN apt-get -y update && apt-get -y install curl && \
    curl -L -o /usr/local/bin/BrowserStackLocal \
        https://s3.amazonaws.com/browserStack/browserstack-local/BrowserStackLocal-linux-x64 && \
    chmod +x /usr/local/bin/BrowserStackLocal

ADD ./browserstack.sh ./

ENTRYPOINT ["./browserstack.sh"]
