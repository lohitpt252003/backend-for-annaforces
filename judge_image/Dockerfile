            FROM ubuntu:22.04
            ENV DEBIAN_FRONTEND=noninteractive
            RUN apt-get update && \
                apt-get install -y --no-install-recommends gcc g++ python3 python3-pip time coreutils && \
                apt-get clean && \
                rm -rf /var/lib/apt/lists/*
            WORKDIR /sandbox/temp
