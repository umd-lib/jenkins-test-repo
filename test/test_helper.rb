# frozen_string_literal: true

require 'simplecov'
require 'simplecov-rcov'
SimpleCov.formatters = [
  SimpleCov::Formatter::HTMLFormatter,
  SimpleCov::Formatter::RcovFormatter
]
SimpleCov.start

ENV['RAILS_ENV'] ||= 'test'
require_relative '../config/environment'
require 'rails/test_help'
require 'minitest/reporters'
Minitest::Reporters.use! [Minitest::Reporters::ProgressReporter.new,
                          Minitest::Reporters::JUnitReporter.new('coverage/junit')]

# A patch to keep Cap setup/teardowns from locking the DB
class ActiveRecord::Base
  mattr_accessor :shared_connection
  @@shared_connection = nil

  def self.connection
    @@shared_connection || retrieve_connection
  end
end
ActiveRecord::Base.shared_connection = ActiveRecord::Base.connection

class ActiveSupport::TestCase
  # Setup all fixtures in test/fixtures/*.yml for all tests in alphabetical order.
  fixtures :all

  # Add more helper methods to be used by all tests here...
  def run_as_user(user)
    user = user.cas_directory_id if user.is_a?(User)
    original_user = session[:cas][:user] if session[:cas] && session[:cas][:user]

    session[:cas] = { user: user }
    begin
      yield user
    ensure
      session[:cas][:user] = original_user
    end
  end

  # this creates a temp user that is destroyed afterwards
  # pass in if it's an admin
  # and the roles by passing in an array of Organizations
  # and the block to yield to run_as_user
  def with_temp_user(admin: false, roles: [])
    user = User.create(cas_directory_id: SecureRandom.hex, name: SecureRandom.hex, admin: admin)
    roles.each { |role| user.roles.create(organization: role) }
    begin
      yield user
    ensure
      user.destroy!
    end
  end
end

class ActionDispatch::IntegrationTest
  def login(user)
    visit '/'
    fill_in 'username', with: user
    fill_in 'password', with: 'any password'
    click_button 'Login'
  end

  def login_admin
    login('admin')
  end

  def login_not_admin
    login('not_admin')
  end
end
