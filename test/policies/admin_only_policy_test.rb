# frozen_string_literal: true

require 'test_helper'

# Tests for AdminOnlyPolicy class
class AdminOnlyPolicyTest < ActiveSupport::TestCase
  def setup
    @admin_user = users(:admin)
    @not_admin_user = users(:not_admin)
  end

  # In the following the "Role" object is used to get the AdminOnlyPolicy
  def test_index
    assert Pundit.policy!(@admin_user, Role).index?
    assert_not Pundit.policy!(@not_admin_user, Role).index?
  end

  def test_show
    assert Pundit.policy!(@admin_user, Role).show?
    assert_not Pundit.policy!(@not_admin_user, Role).show?
  end

  def test_new
    assert Pundit.policy!(@admin_user, Role).new?
    assert_not Pundit.policy!(@not_admin_user, Role).new?
  end

  def test_edit
    assert Pundit.policy!(@admin_user, Role).edit?
    assert_not Pundit.policy!(@not_admin_user, Role).edit?
  end

  def test_create
    assert Pundit.policy!(@admin_user, Role).create?
    assert_not Pundit.policy!(@not_admin_user, Role).create?
  end

  def test_update
    assert Pundit.policy!(@admin_user, Role).update?
    assert_not Pundit.policy!(@not_admin_user, Role).update?
  end

  def test_destroy
    assert Pundit.policy!(@admin_user, Role).destroy?
    assert_not Pundit.policy!(@not_admin_user, Role).destroy?
  end
end
