# frozen_string_literal: true

require 'test_helper'

class HomeControllerTest < ActionController::TestCase
  test 'should not allow unauthenticated users' do
    get :index
    assert_response(401)
  end

  test 'should show "Terms of Service" page if CAS uid is not in system.' do
    builder = CasSessionBuilder.new(session)
    builder.cas_user_name('foobar').cas_uid('NOT_IN_SYSTEM').first_name('Foo').last_name('Bar')

    get :index
    assert_template 'terms_of_service'
  end

  test 'should show "Previously Captured" page if CAS uid is in system.' do
    builder = CasSessionBuilder.new(session)
    builder.cas_user_name('foobar').cas_uid('123456789').first_name('Foo').last_name('Bar')

    get :index
    assert_template 'previously_captured'
  end

  test 'CAS response without UID attribute should show CAS error page.' do
    builder = CasSessionBuilder.new(session)
    builder.cas_user_name('foobar').first_name('Foo').last_name('Bar')

    get :index
    assert_template 'shared/error'
  end
end
