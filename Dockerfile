# Dockerfile for the generating orcid-umd Rails application Docker image
#
# To build:
#
# docker build -t docker.lib.umd.edu/orcid-umd:<VERSION> -f Dockerfile .
#
# where <VERSION> is the Docker image version to create.

FROM ruby:2.6.3-slim

# Install apt based dependencies required to run Rails as
# well as RubyGems. As the Ruby image itself is based on a
# Debian image, we use apt-get to install those.
RUN apt-get update && \
    apt-get install -y build-essential \
                       git \
                       libpq-dev \
                       libsqlite3-dev && \
    apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

# Workaround until https://login.umd.edu gets a better SSL certificate
# This is intended to fix an "OpenSSL::SSL::SSLError (SSL_connect returned=1 errno=0 state=error: dh key too small)"
# error when connecting to https://login.umd.edu
RUN sed '/CipherString = DEFAULT@SECLEVEL=2/d' /etc/ssl/openssl.cnf > /etc/ssl/openssl.cnf.fixed && \
    mv /etc/ssl/openssl.cnf.fixed /etc/ssl/openssl.cnf

# Create a user for the web app.
RUN addgroup --gid 9999 app && \
    adduser --uid 9999 --gid 9999 --disabled-password --gecos "Application" app && \
    usermod -L app

# Configure the main working directory. This is the base
# directory used in any further RUN, COPY, and ENTRYPOINT
# commands.

USER app
WORKDIR /home/app

ENV RAILS_ENV=production

# Copy the Gemfile as well as the Gemfile.lock and install
# the RubyGems. This is a separate step so the dependencies
# will be cached unless changes to one of those two files
# are made.
COPY --chown=app:app Gemfile Gemfile.lock /home/app/webapp/
RUN cd /home/app/webapp && \
    gem install bundler && \
    bundle install --jobs 20 --retry 5 --without development test && \
    cd ..

# Copy the main application.
COPY  --chown=app:app . /home/app/webapp/

# Copy Rails application start script
COPY --chown=app:app docker_config/orcid-umd/rails_start.sh /home/app/webapp

# Leave RAILS_RELATIVE_URL_ROOT and SCRIPT_NAME blank, if application
# is at the host root
ENV RAILS_RELATIVE_URL_ROOT=
ENV SCRIPT_NAME=

# The following SECRET_KEY_BASE and ENV_PROD_DATABASE_ADAPTER
# variables are used so that the "assets:precompile" command
# will run run without throwing an error. They have no effect
# on the application when it is actually run.
ENV SECRET_KEY_BASE=1
ENV PROD_DATABASE_ADAPTER=postgresql
RUN cd /home/app/webapp && \
    bundle exec rails assets:precompile && \
    cd ..

# Expose port 3000 to the Docker host, so we can access it
# from the outside.
EXPOSE 3000

# The main command to run when the container starts.
CMD ["/home/app/webapp/rails_start.sh"]
