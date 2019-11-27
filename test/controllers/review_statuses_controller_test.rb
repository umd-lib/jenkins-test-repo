# frozen_string_literal: true

require 'test_helper'

class ReviewStatusesControllerTest < ActionController::TestCase
  setup do
    @review_status = review_statuses(:under_review)
    @unused_review_status = review_statuses(:never)
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
    assert_not_nil assigns(:review_statuses)
  end

  test 'should get new' do
    get :new
    assert_response :success
  end

  test 'should create review_status' do
    assert_difference('ReviewStatus.count') do
      post :create, params: { review_status: { color: @review_status.color,
                                               name: 'Test Status',
                                               code: 'test' } }
    end

    assert_redirected_to review_status_path(assigns(:review_status))
  end

  test 'should show review_status' do
    get :show, params: { id: @review_status }
    assert_response :success
  end

  test 'should get edit' do
    get :edit, params: { id: @review_status }
    assert_response :success
  end

  test 'should update review_status' do
    patch :update, params: { id: @review_status,
                             review_status: { color: @review_status.color,
                                              name: @review_status.name,
                                              code: @review_status.code } }
    assert_redirected_to review_status_path(assigns(:review_status))
  end

  test 'should destroy review_status' do
    assert_difference('ReviewStatus.count', -1) do
      delete :destroy, params: { id: @unused_review_status }
    end

    assert_redirected_to review_statuses_path
  end

  test 'should show error when cannot destroy review status with associated records' do
    @review_status.reload
    assert_no_difference('ReviewStatus.count') do
      delete :destroy, params: { id: @review_status }
    end
    assert_not flash.empty?

    assert_redirected_to review_statuses_path
  end

  test 'forbid access by non-admin user' do
    run_as_user(users(:not_admin)) do
      get :index
      assert_response :forbidden

      get :new
      assert_response :forbidden

      get :show, params: { id: @review_status }
      assert_response :forbidden

      get :edit, params: { id: @review_status }
      assert_response :forbidden

      post :create, params: { review_status: { color: 'black',
                                               name: @review_status.name,
                                               code: @review_status.code } }
      assert_response :forbidden

      patch :update, params: { id: @review_status,
                               review_status: { color: 'white',
                                                name: @review_status.name,
                                                code: @review_status.code } }
      assert_response :forbidden

      delete :destroy, params: { id: @review_status }
      assert_response :forbidden
    end
  end
end
