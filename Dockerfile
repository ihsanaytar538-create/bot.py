FROM eclipse-temurin:17-jre
WORKDIR /app
RUN curl -L -o Lavalink.jar https://github.com/lavalink-devs/Lavalink/releases/latest/download/Lavalink.jar
COPY application.yml .
CMD ["java", "-jar", "Lavalink.jar"]
