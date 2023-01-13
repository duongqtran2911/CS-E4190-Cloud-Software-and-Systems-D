FROM alpine:3.12
WORKDIR /usr/app
COPY . /usr/app/
ENV VAR 10
RUN chmod +x fibonacci.sh
ENV MSG "Hello Docker!"
RUN chmod +x helloDocker.sh
CMD ["./fibonacci.sh"]