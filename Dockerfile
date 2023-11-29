FROM python:3.8

WORKDIR /up-service

COPY ./requirements.txt /up-service

# Install OpenJDK-17
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get install -y ant && \
    apt-get clean;

# Fix certificate issues
RUN apt-get update && \
    apt-get install ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f;

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64/
RUN export JAVA_HOME

RUN pip3 install -r requirements.txt

# RUN git clone -b v1.0.0 https://github.com/aiplan4eu/unified-planning.git
# RUN pip3 install ./unified-planning[engines]

COPY . /up-service

RUN pip3 install ./unified-planning[engines]

RUN apt-get -y update
RUN apt-get -y install git wget

RUN jupyter trust ./unified-planning/docs/notebooks/*.ipynb

EXPOSE 8061 8062

CMD [ "./start.sh" ]
