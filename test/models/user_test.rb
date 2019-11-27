# frozen_string_literal: true

require 'test_helper'

# Tests for the "User" model
class UserTest < ActiveSupport::TestCase
  def setup
    @user = User.new(cas_directory_id: 'sample_user', name: 'Sample User')
    @division = Organization.find_by(organization_type: Organization.organization_types['division'])
    @department = Organization.find_by(organization_type: Organization.organization_types['department'])
    @unit = Organization.find_by(organization_type: Organization.organization_types['unit'])
  end

  test 'should be valid' do
    assert @user.valid?
  end

  test 'cas_directory_id should be present' do
    @user.cas_directory_id = '  '
    assert_not @user.valid?
  end

  test 'cas_directory_id should be unique' do
    duplicate_user = @user.dup
    duplicate_user.cas_directory_id = @user.cas_directory_id.upcase
    @user.save!
    assert_not duplicate_user.valid?
  end

  test 'name should be present' do
    @user.name = '  '
    assert_not @user.valid?
  end

  test 'admin? should show correct admin status of user' do
    assert_not @user.admin?
    assert users(:admin).admin?
    assert_not users(:not_admin).admin?
  end

  test 'division? should show correct division status of user' do
    user = User.new(cas_directory_id: 'division_user', name: 'Division User')
    assert_not user.division?
    Role.create(user: user, organization: @division)
    assert user.reload.division?
  end

  test 'department? should show correct department status of user' do
    user = User.new(cas_directory_id: 'department_user', name: 'Department User')
    assert_not user.department?
    Role.create(user: user, organization: @department)
    assert user.reload.department?
  end

  test 'unit? should show correct unit status of user' do
    user = User.new(cas_directory_id: 'unit_user', name: 'Unit User')
    assert_not user.unit?
    Role.create(user: user, organization: @unit)
    assert user.reload.unit?
  end

  test 'roles should return roles for the user' do
    assert @user.roles.empty?
    assert_equal 2, users(:two_roles).roles.count
  end

  test 'should be able to delete a user and its roles' do
    user = User.create(cas_directory_id: 'delete_me', name: 'nobody')
    role = Role.create(user: user, organization: @department)

    assert_equal 1, user.roles.count
    assert Role.exists? role.id

    user.destroy
    assert_not User.exists? user.id
    assert_not Role.exists? role.id
  end
end
