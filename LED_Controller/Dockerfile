FROM python:3.12.6-slim-bullseye

WORKDIR /app

ARG ENVIRONMENT=PROD
ARG PORT=8000
ARG VERSION=1.1.0

ENV ENVIRONMENT=$ENVIRONMENT
ENV PORT=$PORT

COPY services/backend/dist/led_controller-$VERSION-py3-none-any.whl .
RUN apt-get update \
    && apt-get install -y \
        gcc \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/ \
    && pip install --no-cache-dir \
        ./led_controller-$VERSION-py3-none-any.whl

# The command might be formatted incorrectly
CMD ["hypercorn", "-w1", "--reload", "-b0.0.0.0:$PORT", "sootworks.led_controller.app:app"]
