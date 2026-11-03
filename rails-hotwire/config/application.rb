require_relative "boot"
require "rails/all"
Bundler.require(*Rails.groups)

module FruehfoerderungPoc
  class Application < Rails::Application
    config.load_defaults 8.1
    config.time_zone = "Europe/Berlin"
    config.i18n.default_locale = :de
    config.active_job.queue_adapter = :async
    # Intentionally a small monolith; Rails autoloads app/services automatically.
  end
end
