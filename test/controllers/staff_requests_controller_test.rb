# frozen_string_literal: true

require 'test_helper'

class StaffRequestsControllerTest < ActionController::TestCase
  # by default these test run as admin.
  setup do
    @staff_request = StaffRequest.first
    @archived_staff_request = ArchivedStaffRequest.first
    session[:cas] = { user: 'admin' }
  end

  test 'should not allow unauthed users' do
    run_as_user(nil) do
      get :index
      assert_response(401)
    end
  end

  test 'should not allow users with bad/fake user accounts' do
    run_as_user('gary') do
      get :index
      assert_response(403)
    end
  end

  test 'should allow authed users index' do
    get :index
    assert_response(200)
    assert assigns(:model_klass), StaffRequest
    assert_not_nil assigns(:requests)
  end

  test 'should allow authed users to new' do
    get :new
    assert_response(200)
  end

  test 'should show staff_request' do
    get :show, params: { id: @staff_request }
    assert_response :success
  end

  test 'should create staff_request' do
    assert_difference('Request.count') do
      post :create, params: { staff_request: {
        contractor_name: @staff_request.contractor_name,
        organization_id: @staff_request.organization_id,
        employee_type: @staff_request.employee_type,
        employee_name: @staff_request.employee_name,
        hours_per_week: @staff_request.hours_per_week,
        justification: @staff_request.justification,
        annual_base_pay: @staff_request.annual_base_pay,
        nonop_funds: @staff_request.nonop_funds,
        nonop_source: @staff_request.nonop_source,
        number_of_positions: @staff_request.number_of_positions,
        number_of_weeks: @staff_request.number_of_weeks,
        position_title: @staff_request.position_title,
        request_type: @staff_request.request_type
      } }
    end

    assert_redirected_to staff_request_path(assigns(:request))
    assert assigns(:model_klass), StaffRequest
    assert_instance_of StaffRequest, assigns(:request)
  end

  test 'should not create invalid staff_request' do
    assert_no_difference('Request.count') do
      post :create, params: {  staff_request: {
        contractor_name: nil,
        organization_id: nil,
        employee_type: nil,
        hours_per_week: nil,
        justification: nil,
        nonop_funds: nil,
        nonop_source: nil,
        number_of_positions: nil,
        number_of_weeks: nil,
        position_title: nil,
        request_type: nil
      } }
    end
  end

  test 'should create/update contractor_request but without admin only values when not admin' do
    run_as_user(:not_admin) do |user|
      unit = users(user).organizations.find(&:unit?)
      org = unit.parent
      assert_difference('Request.count') do
        post :create, params: { staff_request: {
          contractor_name: @staff_request.contractor_name,
          organization_id: org,
          unit_id: unit,
          employee_type: @staff_request.employee_type,
          employee_name: @staff_request.employee_name,
          hours_per_week: @staff_request.hours_per_week,
          justification: @staff_request.justification,
          annual_base_pay: @staff_request.annual_base_pay,
          nonop_funds: @staff_request.nonop_funds,
          nonop_source: @staff_request.nonop_source,
          number_of_positions: @staff_request.number_of_positions,
          number_of_weeks: @staff_request.number_of_weeks,
          position_title: @staff_request.position_title,
          request_type: @staff_request.request_type,
          review_status_id: review_statuses(:approved),
          review_comment: 'Hey hey hey'
        } }
      end

      assert_redirected_to staff_request_path(assigns(:request))
      assert_equal review_statuses(:under_review).id, assigns(:request).review_status_id
      assert_nil assigns(:request).review_comment
    end
  end

  test 'should update staff_request' do
    patch :update, params: { id: @staff_request, staff_request: {
      contractor_name: @staff_request.contractor_name,
      organization_id: @staff_request.organization_id,
      employee_type: @staff_request.employee_type,
      hours_per_week: @staff_request.hours_per_week,
      justification: @staff_request.justification,
      nonop_funds: @staff_request.nonop_funds,
      nonop_source: @staff_request.nonop_source,
      number_of_positions: @staff_request.number_of_positions,
      number_of_weeks: @staff_request.number_of_weeks,
      position_title: @staff_request.position_title,
      request_type: @staff_request.request_type,
      review_status_id: @staff_request.review_status_id,
      review_comment: @staff_request.review_comment
    } }
    assert_redirected_to staff_request_path(assigns(:request))
  end

  test 'should not update an invalid staff_request' do
    original_attrs = @staff_request.attributes
    patch :update, params: { id: @staff_request, staff_request: {
      contractor_name: nil, organization_id: nil, employee_type: nil,
      hours_per_week: nil, justification: nil,
      nonop_funds: nil, nonop_source: nil, number_of_positions: nil,
      number_of_weeks: nil, position_title: nil, request_type: nil,
      review_status_id: nil, review_comment: nil
    } }
    assert_equal original_attrs, StaffRequest.find(@staff_request.id).attributes
  end

  test 'should destroy staff_request' do
    assert_difference('Request.count', -1) do
      delete :destroy, params: { id: @staff_request }
    end

    assert_redirected_to staff_requests_path
  end

  # ArchivedstaffRequests
  test 'should allow users to see archive' do
    get :index, params: { archive: true }
    assert_response(200)
    assert assigns(:model_klass), StaffRequest
    assert_not_nil assigns(:requests)
  end

  test 'should show archived staff request' do
    get :show, params: { id: @archived_staff_request }
    assert_response :success
  end
end
