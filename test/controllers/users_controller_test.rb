# frozen_string_literal: true

require 'test_helper'

class UsersControllerTest < ActionController::TestCase
  setup do
    session[:cas] = { user: 'admin' }
    @user = users(:red_shirt)
  end

  test 'should get index' do
    get :index
    assert_response :success
    assert_not_nil assigns(:users)
  end

  test 'should get new' do
    get :new
    assert_response :success
  end

  test 'should create user' do
    assert_difference('User.count') do
      post :create, params: { user: { cas_directory_id: 'NEW_USER', name: 'New User' } }
    end

    assert_redirected_to user_path(assigns(:user))
  end

  test 'should show user' do
    get :show, params: { id: @user }
    assert_response :success
  end

  test 'should get edit' do
    get :edit, params: { id: @user }
    assert_response :success
  end

  test 'should update user' do
    patch :update, params: { id: @user, user: { cas_directory_id: @user.cas_directory_id, name: @user.name } }
    assert_redirected_to user_path(assigns(:user))
  end

  test 'should destroy user' do
    user = User.create(cas_directory_id: 'SAMPLE_USER', name: 'Sample User')
    assert_difference('User.count', -1) do
      delete :destroy, params: { id: user }
    end

    assert_redirected_to users_path
  end

  test 'allow access by non-admin user to see and edit own entry' do
    not_admin_user = users(:not_admin)
    run_as_user(not_admin_user) do
      get :show, params: { id: not_admin_user }
      assert_response :success

      get :edit, params: { id: not_admin_user }
      assert_response :success

      patch :update, params: { id: not_admin_user,
                               user: { cas_directory_id: not_admin_user.cas_directory_id,
                                       name: not_admin_user.name } }
      assert_redirected_to user_path(not_admin_user)
    end
  end

  test 'forbid access by non-admin user' do
    run_as_user(users(:not_admin)) do
      get :index
      assert_response :forbidden

      get :new
      assert_response :forbidden

      get :show, params: { id: @user }
      assert_response :forbidden

      get :edit, params: { id: @user }
      assert_response :forbidden

      post :create, params: { user: { cas_directory_id: 'NEW_USER', name: 'New User' } }
      assert_response :forbidden

      patch :update, params: { id: @user, user: { cas_directory_id: @user.cas_directory_id, name: @user.name } }
      assert_response :forbidden

      delete :destroy, params: { id: @user }
      assert_response :forbidden
    end
  end

  test 'can logout' do
    get :logout
    assert_nil session[:cas]
  end
end
