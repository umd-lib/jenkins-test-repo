# frozen_string_literal: true

require 'application_system_test_case'

class OrganizationEditTest < ApplicationSystemTestCase
  def setup
    login_admin
  end

  test 'should disable links when in detail page' do
    click_link 'admin'
    click_link 'Manage Organizations'

    click_link 'Administrative Services (ASD)'
    assert page.has_link?('Add Member')
    assert page.has_button?('Active')
    assert page.has_button?('Deactive')
    assert page.has_selector?('input[type=submit]:not([disabled])')

    # when we visit the nonedit page these links should not be there
    visit current_url.gsub('/edit', '')
    assert_not page.has_link?('Add Member')
    assert_not page.has_button?('Active')
    assert_not page.has_button?('Deactive')
    assert_not page.has_selector?('input[type=submit]:not([disabled])')
  end
end
