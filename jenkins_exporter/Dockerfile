FROM python:3.7-alpine

RUN mkdir -p /app/jenkins_exporter
WORKDIR /app/jenkins_exporter

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py /app/jenkins_exporter

EXPOSE 9118

ENTRYPOINT [ "python", "-m", "jenkins_exporter" ]
