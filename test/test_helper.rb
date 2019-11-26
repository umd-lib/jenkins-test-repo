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
Minitest::Reporters.use! [Minitest::Reporters::DefaultReporter.new(color: true),
                          Minitest::Reporters::JUnitReporter.new('coverage/junit')]

class ActiveSupport::TestCase
  # Setup all fixtures in test/fixtures/*.yml for all tests in alphabetical order.
  fixtures :all

  # Add more helper methods to be used by all tests here...

  # Sample settings for CAS attributes
  ENV['CAS_SESSION_ATTRIBUTE'] = 'cas'
  ENV['CAS_UID_ATTRIBUTE'] = 'uid'
  ENV['CAS_FIRST_NAME_ATTRIBUTE'] = 'firstName'
  ENV['CAS_LAST_NAME_ATTRIBUTE'] = 'lastName'

  # Fluent interface for building a CAS session for testing
  #
  # builder = CasSessionBuilder.new(session)
  # builder.cas_user_name('foobar').cas_uid('123456789').first_name('Foo').last_name('Bar')
  class CasSessionBuilder
    def initialize(session)
      @session = session
      @session[ENV['CAS_SESSION_ATTRIBUTE']] ||= {}
      @session[ENV['CAS_SESSION_ATTRIBUTE']]['extra_attributes'] ||= {}
    end

    def cas_user_name(cas_user_name)
      @session[ENV['CAS_SESSION_ATTRIBUTE']]['user'] = cas_user_name
      self
    end

    def cas_uid(cas_uid)
      @session[ENV['CAS_SESSION_ATTRIBUTE']]['extra_attributes'][ENV['CAS_UID_ATTRIBUTE']] = cas_uid
      self
    end

    def first_name(first_name)
      @session[ENV['CAS_SESSION_ATTRIBUTE']]['extra_attributes'][ENV['CAS_FIRST_NAME_ATTRIBUTE']] = first_name
      self
    end

    def last_name(last_name)
      @session[ENV['CAS_SESSION_ATTRIBUTE']]['extra_attributes'][ENV['CAS_LAST_NAME_ATTRIBUTE']] = last_name
      self
    end
  end
end
