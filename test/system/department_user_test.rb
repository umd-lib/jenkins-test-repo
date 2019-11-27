# frozen_string_literal: true

require 'application_system_test_case'

class DepartmentUserTest < ApplicationSystemTestCase
  def setup
    login('middle_mgmt')

    @user = users(:middle_mgmt)
    @dept = @user.organizations.find(&:department?)
  end

  test 'should allow unit to be optional if the user has non-unit roles' do
    click_link 'Labor and Assistance'
    click_link 'New'

    select 'Faculty', from: 'Employee type'
    select 'New', from: 'Request type'
    fill_in 'Contractor name', with: SecureRandom.hex
    fill_in 'Number of positions', with: 1
    fill_in 'Hours per week', with: '9.99'
    fill_in 'Hourly rate', with: '9.99'
    fill_in 'Number of weeks', with: '9'
    select @dept.name, from: 'Department'
    fill_in 'Justification', with: 'This is a test'
    fill_in 'Position title', with: SecureRandom.hex
    find('.page-header .btn-success').click

    assert page.has_content?('Labor and Assistance Requests successfully created.')
    assert_not page.has_content?('Unit is required for users with only Unit permissions')
  end

  test 'should allow department user to make a unit request even if past unit deadline' do
    cutoff = OrganizationCutoff.find(OrganizationCutoff.organization_types['unit'])
    cutoff.cutoff_date = cutoff.cutoff_date - 1.year
    cutoff.save
    unit = @dept.organizations.find(&:unit?)

    click_link 'Labor and Assistance'
    click_link 'New'

    select 'Faculty', from: 'Employee type'
    select 'New', from: 'Request type'
    fill_in 'Contractor name', with: SecureRandom.hex
    fill_in 'Number of positions', with: 1
    fill_in 'Hours per week', with: '9.99'
    fill_in 'Hourly rate', with: '9.99'
    fill_in 'Number of weeks', with: '9'
    select @dept.name, from: 'Department'
    select unit.name, from: 'Unit'
    fill_in 'Justification', with: 'This is a test'
    fill_in 'Position title', with: SecureRandom.hex
    find('.page-header .btn-success').click

    assert page.has_content?('Labor and Assistance Requests successfully created.')
    assert_not page.has_content?('Unit is required for users with only Unit permissions')
    assert_not page.has_content?('The submission window for this request has ended.')
  end
end
