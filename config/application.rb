require_relative 'boot'

require 'rails/all'
require 'rack-cas/session_store/active_record'

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module OrcidUmd
  class Application < Rails::Application
    # Initialize configuration defaults for originally generated Rails version.
    config.load_defaults 5.2

    # Settings in config/environments/* take precedence over those specified here.
    # Application configuration can go into files in config/initializers
    # -- all .rb files in that directory are automatically loaded after loading
    # the framework and any gems in your application.

    config.rack_cas.server_url = ENV['CAS_SERVER_URL']

    # Ensure CAS_SERVER_URL is defined, as otherwise CAS authentication will
    # not occur. Skip when not running as a server so assets:precompile can
    # be performed.
    if ((Rails.const_defined? 'Server') && config.rack_cas.server_url.to_s.strip.empty?)
      puts("ERROR: CAS_SERVER_URL environment variable is not configured.")
      exit 1
    end

    config.rack_cas.session_store = RackCAS::ActiveRecordStore
  end
end
