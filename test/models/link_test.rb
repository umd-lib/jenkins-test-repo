# frozen_string_literal: true

require 'test_helper'

# Tests for the "User" model
class LinkTest < ActiveSupport::TestCase
  test 'should be valid' do
    link = Link.new(text: SecureRandom.hex, url: 'http://umd.edu')
    assert link.valid?
  end

  test 'link and name should be present' do
    link = Link.new(url: 'http://umd.edu')
    assert_not link.valid?
    link = Link.new(text: SecureRandom.hex)
    assert_not link.valid?
  end

  test 'url should be http or https' do
    link = Link.new(text: SecureRandom.hex, url: SecureRandom.hex)
    assert_not link.valid?
    link.url = 'http://umd.edu'
    assert link.valid?
  end
end
