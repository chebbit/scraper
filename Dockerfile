FROM python:3.7-stretch

LABEL maintainer="dancetj@gmail.com"

RUN apt-get update -y && \
	apt-get install -y \
	    nano \
		cron \
		supervisor && \
	rm -rf /var/lib/apt/lists/*

COPY src /app
WORKDIR /app

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN pip install -r /app/requirements.txt
RUN echo "*/1 * * * * cd /app && /usr/local/bin/python cli.py run-scraper >> /app/cron.log 2>&1" | crontab -

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

