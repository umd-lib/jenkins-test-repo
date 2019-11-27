# frozen_string_literal: true

require 'test_helper'

# Tests for PersonnelRequestPolicy's Scope class
# These tests only cover visibility of the personnel requests, not the
# actions that can be taken on them.
class ArchivedRequestPolicyScopeTest < ActiveSupport::TestCase
  def setup; end

  test 'user w/out roles cannot update, edit, delete, show' do
    with_temp_user do |temp_user|
      assert_not Pundit.policy!(temp_user, ArchivedLaborRequest.new).update?
      assert_not Pundit.policy!(temp_user, ArchivedLaborRequest.new).edit?
      assert_not Pundit.policy!(temp_user, ArchivedLaborRequest.new).destroy?
      assert_not Pundit.policy!(temp_user, ArchivedLaborRequest.new).show?
    end
  end

  test 'admin cannot update, edit, delete but can show' do
    with_temp_user(admin: true) do |temp_user|
      assert_not Pundit.policy!(temp_user, ArchivedLaborRequest.new).update?
      assert_not Pundit.policy!(temp_user, ArchivedLaborRequest.new).edit?
      assert_not Pundit.policy!(temp_user, ArchivedLaborRequest.new).destroy?
      assert Pundit.policy!(temp_user, ArchivedLaborRequest.new).show?
    end
  end

  test 'unit users should see unit requests' do
    org = ArchivedLaborRequest.where.not(unit_id: nil).first.unit
    unit_requests = ArchivedLaborRequest.where(unit_id: org.id).pluck :id

    with_temp_user(admin: false, roles: [org]) do |temp_user|
      scoped = ArchivedRequestPolicy::Scope.new(temp_user, ArchivedLaborRequest).resolve.pluck :id
      assert_equal unit_requests, scoped
    end
  end
end
