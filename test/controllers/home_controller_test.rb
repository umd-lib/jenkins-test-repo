# frozen_string_literal: true

require 'test_helper'

class HomeControllerTest < ActionController::TestCase
  test 'should not allow unauthed users' do
    get :index
    assert_response(401)
  end

  test 'should allow authed users' do
    run_as_user('not_admin') do
      get :index
      assert_response(:success)
    end
  end

  test 'should allow users to export their records' do
    user_id, rcount = Request.pluck(:user_id).group_by(&:itself)
                             .map { |k, v| [k, v.count] }.max_by { |_k, v| v }
    user = User.find user_id
    run_as_user(user) do
      get :index, format: 'xlsx'
      assert_response :success
      file = Tempfile.new(['test_temp', '.xlsx'])
      # don't trust counter_case when using fixtures.
      begin
        file.write response.body
        file.close
        spreadsheet = Roo::Excelx.new(file.path)
        expected_row_count = rcount + 1 # include header row in count
        assert rcount > 1, 'There are no labor requests'
        assert_equal expected_row_count, spreadsheet.last_row
      ensure
        file.delete
      end
    end
  end
end
