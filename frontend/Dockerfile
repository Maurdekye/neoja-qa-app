FROM ghcr.io/cirruslabs/flutter:3.27.3 as build-env

ARG FLASK_API_BASE_URL

WORKDIR /app

COPY pubspec.yaml /app

RUN flutter pub get

COPY . /app

RUN echo "$FLASK_API_BASE_URL"

RUN flutter build web \
    --release \
    --dart-define=FLASK_API_BASE_URL=$FLASK_API_BASE_URL

FROM nginx:alpine
COPY --from=build-env /app/build/web /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]