# frozen_string_literal: true

require 'test_helper'

# Tests for ReportPolicy class
class ReportPolicyTest < ActiveSupport::TestCase
  def setup
    @admin_user = users(:admin)
  end

  def test_edit
    assert_not Pundit.policy!(@admin_user, Report).edit?
  end
end
