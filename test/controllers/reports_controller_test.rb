# frozen_string_literal: true

require 'test_helper'

class ReportsControllerTest < ActionController::TestCase
  setup do
    session[:cas] = { user: 'admin' }
    @report = reports(:requests_by_type)
  end

  test 'should get index' do
    get :index
    assert_response :success
    assert_not_nil assigns(:reports)
  end

  test 'should get new' do
    get :new
    assert_response :success
  end

  test 'should create report' do
    assert_difference('Report.count') do
      post :create, params: {
        report: {
          format: :xlsx,
          name: 'RequestsByTypeReport'
        }
      }
    end
    assert_redirected_to report_path(assigns(:report))
  end

  test 'should not create invalid report' do
    assert_no_difference('Report.count') do
      post :create, params: { report: {
        format: nil
      } }
    end
  end

  test 'should show contractor_request' do
    get :show, params: { id: @report }
    assert_response :success
  end

  test 'should get edit' do
    get :edit, params: { id: @report }
    assert_redirected_to report_path(@report)
  end

  test 'should download the output' do
    ReportJob.perform_later @report
    get :download, params: { id: @report, format: :xlsx }
    assert_response :success
  end

  test 'should not allow updated' do
    patch :update, params: { id: @report }
    assert_response :missing
  end

  test 'should destroy a report' do
    trash = reports(:report_with_error)
    assert_difference('Report.count', -1) do
      delete :destroy, params: { id: trash }
    end
    assert_redirected_to reports_path
  end
end
