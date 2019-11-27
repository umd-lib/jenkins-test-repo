# frozen_string_literal: true

require 'application_system_test_case'

class UnitUserTest < ApplicationSystemTestCase
  def setup
    login_not_admin

    @user = users(:not_admin)
    @unit = @user.organizations.find(&:unit?)
  end

  test 'should require a unit if the user is a unit user' do
    click_link 'Labor and Assistance'
    click_link 'New'

    select 'Faculty', from: 'Employee type'
    select 'New', from: 'Request type'
    fill_in 'Contractor name', with: SecureRandom.hex
    fill_in 'Number of positions', with: 1
    fill_in 'Hours per week', with: '9.99'
    fill_in 'Hourly rate', with: '9.99'
    fill_in 'Number of weeks', with: '9'
    select @unit.parent.name, from: 'Department'
    fill_in 'Justification', with: 'This is a test'
    fill_in 'Position title', with: SecureRandom.hex
    find('.page-header .btn-success').click

    assert_not page.has_content?('Labor and Assistance Requests successfully created.')
    assert page.has_content?('Unit is required for users with only Unit permissions')

    select @unit.name, from: 'Unit'
    find('.page-footer .btn-success').click

    assert page.has_content?('Labor and Assistance Requests successfully created.')
    assert_not page.has_content?('Unit is required for users with only Unit permissions')
  end

  test 'should require a unit if the user is a unit user when editing' do
    # First, create a new request
    click_link 'Labor and Assistance'
    click_link 'New'

    assert_not page.has_content?('The submission window for this request has ended')

    position_title = SecureRandom.hex

    select 'Faculty', from: 'Employee type'
    select 'New', from: 'Request type'
    fill_in 'Contractor name', with: SecureRandom.hex
    fill_in 'Number of positions', with: 1
    fill_in 'Hours per week', with: '9.99'
    fill_in 'Hourly rate', with: '9.99'
    fill_in 'Number of weeks', with: '9'
    select @unit.parent.name, from: 'Department'
    fill_in 'Justification', with: 'This is a test'
    fill_in 'Position title', with: position_title
    select @unit.name, from: 'Unit'
    find('.page-footer .btn-success').click

    assert page.has_content?('Labor and Assistance Requests successfully created.')

    # Edit the request, unsetting the "Unit" field
    click_link 'Edit', match: :first
    select '', from: 'Unit'
    find('.page-footer .btn-success').click

    assert_not page.has_content?('The submission window for this request has ended')
    assert_not page.has_content?("#{position_title} successfully updated.")
    assert page.has_content?('Unit is required for users with only Unit permissions')
  end

  test 'should require a unit if the user has both department and unit roles' do
    # For this test, the user has a department role, and a unit role, with the
    # unit role being in a different department from the department role.
    #
    # The user should NOT be able to create a request in the unit's department
    # without also specifying the unit.

    # Clear any existing user roles
    Role.where(user: @user).destroy_all
    assert_empty Role.where(user: @user)

    # Find a department, and a unit in a different department
    department = Organization.department.first
    unit = Organization.unit.find { |u| u.parent != department }
    assert_not_equal department, unit.parent

    # Add departmental and unit roles
    Role.create(user: @user, organization: department)
    Role.create(user: @user, organization: unit)
    assert_equal 2, @user.reload.roles.count

    # Attempt to create a request using the unit's department, without the unit
    # being specified.

    click_link 'Labor and Assistance'
    click_link 'New'

    position_title = SecureRandom.hex

    select 'Faculty', from: 'Employee type'
    select 'New', from: 'Request type'
    fill_in 'Contractor name', with: SecureRandom.hex
    fill_in 'Number of positions', with: 1
    fill_in 'Hours per week', with: '9.99'
    fill_in 'Hourly rate', with: '9.99'
    fill_in 'Number of weeks', with: '9'
    select unit.parent.name, from: 'Department'
    fill_in 'Justification', with: 'This is a test'
    fill_in 'Position title', with: position_title
    find('.page-footer .btn-success').click

    assert_not page.has_content?('Labor and Assistance Requests successfully created.')
    assert page.has_content?('Unit is required for users with only Unit permissions')
  end
end
