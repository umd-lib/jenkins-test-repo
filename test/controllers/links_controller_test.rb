# frozen_string_literal: true

require 'test_helper'

class LinksControllerTest < ActionController::TestCase
  setup do
    @link = links(:umd)
    session[:cas] = { user: 'admin' }
  end

  test 'should not allow unauthed users' do
    run_as_user(nil) do
      get :index
      assert_response(401)
    end
  end

  test 'should get index' do
    get :index
    assert_response :success
    assert_not_nil assigns(:links)
  end

  test 'should get new' do
    get :new
    assert_response :success
  end

  test 'should create link' do
    assert_difference('Link.count') do
      post :create, params: { link: { text: 'Test Status', url: 'http://moo.ru' } }
    end
    assert_redirected_to link_path(assigns(:link))
  end

  test 'should show link' do
    get :show, params: { id: @link }
    assert_response :success
  end

  test 'should get edit' do
    get :edit, params: { id: @link }
    assert_response :success
  end

  test 'should update link' do
    patch :update, params: { id: @link, link: { text: 'Take 2', url: 'http://bark.nu' } }
    assert_redirected_to link_path(assigns(:link))
  end

  test 'should destroy link' do
    assert_difference('Link.count', -1) do
      delete :destroy, params: { id: @link }
    end

    assert_redirected_to links_path
  end

  test 'forbid access by non-admin user' do
    run_as_user(users(:not_admin)) do
      get :index
      assert_response :forbidden

      get :new
      assert_response :forbidden

      get :show, params: { id: @link }
      assert_response :forbidden

      get :edit, params: { id: @link }
      assert_response :forbidden

      post :create, params: { link: { text: '1', url: 'http://meow.no' } }
      assert_response :forbidden

      patch :update, params: { id: @link,
                               link: { text: '3', url: 'http://tweet.ca' } }
      assert_response :forbidden

      delete :destroy, params: { id: @link }
      assert_response :forbidden
    end
  end
end
