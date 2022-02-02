# The tag here should match the Meteor version of your app
# per .meteor/release
FROM geoffreybooth/meteor-base:2.2

WORKDIR /app 

# also expose mongodb port
EXPOSE 3001

# ARG gif_monitor
# ENV METEOR_APP_SOURCES=$gif_monitor

# # Copy gif monitor source into container
# RUN echo $METEOR_APP_SOURCES > echo.txt
# RUN echo $gif_monitor >> echo.txt
# RUN echo $PWD >> echo.txt

COPY ./ /app/

RUN meteor npm install

CMD ["meteor", "run"]
