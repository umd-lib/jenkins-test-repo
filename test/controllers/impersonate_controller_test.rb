# frozen_string_literal: true

require 'test_helper'

class ImpersonateControllerTest < ActionController::TestCase
  def setup
    session[:cas] = { user: 'admin' }
    @admin_user = users(:admin)
    @impersonated_user = users(:not_admin)
  end

  test 'create should impersonate user' do
    run_as_user(@admin_user) do
      get :create, params: { user_id: @impersonated_user.id }
      assert_not_nil session[ImpersonateController::IMPERSONATE_USER_PARAM]
      assert_equal session[ImpersonateController::IMPERSONATE_USER_PARAM], @impersonated_user.id
    end
  end

  test 'create should do nothing when given invalid user id' do
    run_as_user(@admin_user) do
      get :create, params: { user_id: 'invalid_user_id' }
      assert_nil session[ImpersonateController::IMPERSONATE_USER_PARAM]
    end
  end

  test 'destroy should stop impersonate user' do
    run_as_user(@admin_user) do
      get :create, params: { user_id: @impersonated_user }
      assert_not_nil session[ImpersonateController::IMPERSONATE_USER_PARAM]
      assert_equal session[ImpersonateController::IMPERSONATE_USER_PARAM], @impersonated_user.id

      delete :destroy
      assert_nil session[ImpersonateController::IMPERSONATE_USER_PARAM]
    end
  end

  test 'access allowed to destroy by non-admin user' do
    run_as_user(users(:not_admin)) do
      delete :destroy
      assert_redirected_to root_path
    end
  end

  test 'should not be allowed to impersonate yourself' do
    run_as_user(@admin_user) do
      get :create, params: { user_id: @admin_user }
      assert_response :forbidden
    end
  end

  test 'should not be allowed to impersonate another admin' do
    with_temp_user(admin: true) do |other_admin|
      run_as_user(@admin_user) do
        get :create, params: { user_id: other_admin }
        assert_response :forbidden
      end
    end
  end
end
