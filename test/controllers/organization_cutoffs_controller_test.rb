# frozen_string_literal: true

require 'test_helper'

class OrganizationCutoffsControllerTest < ActionController::TestCase
  # by default these test run as admin.
  setup do
    @cutoff = OrganizationCutoff.first
    session[:cas] = { user: 'admin' }
  end

  test 'should not allow unauthed users' do
    run_as_user(nil) do
      get :index
      assert_response(401)
    end
  end

  test 'should not allow non-admin users' do
    run_as_user('not_admin') do
      get :index
      assert_response(403)
    end
  end

  test 'should get index' do
    get :index
    assert_response :success
    assert_not_nil assigns(:cutoffs)
  end

  test 'should update role_cutoff' do
    patch :update, params: {
      id: @cutoff,
      organization_cutoff: { cutoff_date: Time.zone.now }
    }
    assert_redirected_to organization_cutoffs_path
  end
end
