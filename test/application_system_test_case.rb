# frozen_string_literal: true

require 'test_helper'

class ApplicationSystemTestCase < ActionDispatch::SystemTestCase
  # Enable headless Chrome to download files to a specified directory
  # See https://gist.github.com/bbonamin/4b01be9ed5dd1bdaf909462ff4fdca95
  DOWNLOAD_DIR = File.join(Dir.tmpdir, 'downloads')

  Capybara.register_driver :chrome_headless do |app|
    options = ::Selenium::WebDriver::Chrome::Options.new

    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1400,1400')

    options.add_preference(:download, prompt_for_download: false,
                                      default_directory: DOWNLOAD_DIR)

    driver = Capybara::Selenium::Driver.new(app, browser: :chrome, options: options)

    # Allow file downloads in Google Chrome when headless
    # https://bugs.chromium.org/p/chromium/issues/detail?id=696481#c89
    bridge = driver.browser.send(:bridge)

    path = "/session/#{bridge.session_id}/chromium/send_command"

    bridge.http.call(:post, path, cmd: 'Page.setDownloadBehavior',
                                  params: {
                                    behavior: 'allow',
                                    downloadPath: DOWNLOAD_DIR
                                  })
    driver
  end

  driven_by :chrome_headless

  def javascript_errors
    page.driver.browser.manage.logs.get(:browser)
        .select { |e| e.level == 'SEVERE' && e.message.present? }
        .collect(&:message)
  end

  def javascript_errors?
    errors = javascript_errors # if you get the log, you clear the log...
    raise JavaScriptError, errors.join("\n\n") if errors.present?
  end

  def teardown
    javascript_errors?
  end
end

class JavaScriptError < StandardError; end
