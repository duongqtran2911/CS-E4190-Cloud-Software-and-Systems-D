#########################
# Enter your code below #
#########################
FROM python:3.10.8-alpine3.16
WORKDIR /usr/app
COPY requirements.txt ./
RUN apk add --no-cache gcc libc-dev linux-headers zlib-dev jpeg-dev libjpeg
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]