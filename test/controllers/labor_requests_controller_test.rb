# frozen_string_literal: true

require 'test_helper'

class LaborRequestsControllerTest < ActionController::TestCase
  # by default these test run as admin.
  setup do
    @labor_request = LaborRequest.first
    @archived_labor_request = ArchivedLaborRequest.first
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
    assert assigns(:model_klass), LaborRequest
    assert_not_nil assigns(:requests)
  end

  test 'should allow authed users to new' do
    get :new
    assert_response(200)
  end

  test 'should show labor_request' do
    get :show, params: { id: @labor_request }
    assert_response :success
  end

  test 'should edit labor_request' do
    get :edit, params: { id: @labor_request }
    assert_response :success
  end

  test 'should create labor_request' do
    assert_difference('Request.count') do
      post :create, params: { labor_request: {
        contractor_name: @labor_request.contractor_name,
        organization_id: @labor_request.organization_id,
        employee_type: @labor_request.employee_type,
        hourly_rate: @labor_request.hourly_rate,
        hours_per_week: @labor_request.hours_per_week,
        justification: @labor_request.justification,
        nonop_funds: @labor_request.nonop_funds,
        nonop_source: @labor_request.nonop_source,
        number_of_positions: @labor_request.number_of_positions,
        number_of_weeks: @labor_request.number_of_weeks,
        position_title: @labor_request.position_title,
        request_type: @labor_request.request_type
      } }
    end

    assert_redirected_to labor_request_path(assigns(:request))
    assert assigns(:model_klass), LaborRequest
    assert_instance_of LaborRequest, assigns(:request)
  end

  test 'should not create invalid labor_request' do
    assert_no_difference('LaborRequest.count') do
      post :create, params: { labor_request: {
        contractor_name: nil,
        organization_id: nil,
        employee_type: nil,
        hourly_rate: nil,
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
        post :create, params: { labor_request: {
          contractor_name: @labor_request.contractor_name,
          organization_id: org,
          unit_id: unit,
          employee_type: @labor_request.employee_type,
          hourly_rate: @labor_request.hourly_rate,
          hours_per_week: @labor_request.hours_per_week,
          justification: @labor_request.justification,
          nonop_funds: @labor_request.nonop_funds,
          nonop_source: @labor_request.nonop_source,
          number_of_positions: @labor_request.number_of_positions,
          number_of_weeks: @labor_request.number_of_weeks,
          position_title: @labor_request.position_title,
          request_type: @labor_request.request_type,
          review_status_id: review_statuses(:approved),
          review_comment: 'Hey hey hey'
        } }
      end

      assert_redirected_to labor_request_path(assigns(:request))
      assert_equal review_statuses(:under_review).id, assigns(:request).review_status_id
      assert_nil assigns(:request).review_comment
    end
  end

  test 'should update labor_request' do
    patch :update, params: { id: @labor_request, labor_request: {
      contractor_name: @labor_request.contractor_name,
      organization_id: @labor_request.organization_id,
      employee_type: @labor_request.employee_type,
      hourly_rate: @labor_request.hourly_rate,
      hours_per_week: @labor_request.hours_per_week,
      justification: @labor_request.justification,
      nonop_funds: @labor_request.nonop_funds,
      nonop_source: @labor_request.nonop_source,
      number_of_positions: @labor_request.number_of_positions,
      number_of_weeks: @labor_request.number_of_weeks,
      position_title: @labor_request.position_title,
      request_type: @labor_request.request_type,
      review_status_id: @labor_request.review_status_id,
      review_comment: @labor_request.review_comment
    } }
    assert_redirected_to labor_request_path(assigns(:request))
  end

  test 'should update labor_request with json' do
    a_different_status = ReviewStatus.where.not(id: @labor_request.review_status_id).sample
    patch :update, format: :json, params: { id: @labor_request,
                                            labor_request: { review_status_id: a_different_status.id } }
    assert_response :success
    assert_equal assigns(:request).review_status_id, a_different_status.id
  end

  test 'should not update an invalid labor_request' do
    original_attrs = @labor_request.attributes
    patch :update, params: { id: @labor_request, labor_request: {
      contractor_name: nil, organization_id: nil, employee_type: nil,
      hourly_rate: nil, hours_per_week: nil, justification: nil,
      nonop_funds: nil, nonop_source: nil, number_of_positions: nil,
      number_of_weeks: nil, position_title: nil, request_type: nil,
      review_status_id: nil, review_comment: nil
    } }
    assert_equal original_attrs, LaborRequest.find(@labor_request.id).attributes
  end

  test 'should destroy labor_request' do
    assert_difference('Request.count', -1) do
      delete :destroy, params: { id: @labor_request }
    end

    assert_redirected_to labor_requests_path
  end

  test 'xlsx format should include all records, even from second page' do
    get :index, params: { page: '2', format: 'xlsx' }

    file = Tempfile.new(['test_temp', '.xlsx'])
    begin
      file.write response.body
      file.close
      spreadsheet = Roo::Excelx.new(file.path)

      num_labor_requests = LaborRequest.count
      expected_row_count = num_labor_requests + 1 # include header row in count
      assert num_labor_requests > 1, 'There are no labor requests'
      assert_equal expected_row_count, spreadsheet.last_row
    ensure
      file.delete
    end
    assert_response :success
  end

  # ArchivedLaborRequests
  test 'should allow users to see archive' do
    get :index, params: { archive: true }
    assert_response(200)
    assert assigns(:model_klass), LaborRequest
    assert_not_nil assigns(:requests)
  end

  test 'should show archived labor request' do
    get :show, params: { id: @archived_labor_request }
    assert_response :success
  end
end
