# frozen_string_literal: true

require 'application_system_test_case'

class WordCountTest < ApplicationSystemTestCase
  def setup
    login_admin
  end

  test 'should count the words in the justification field' do
    click_link 'Labor and Assistance'
    click_link 'New'
    words = ' word ' * 100
    fill_in 'Justification', with: words
    assert page.has_content?('25 words remaining')
    fill_in 'Justification', with: words + words
    assert page.has_content?('Limit exceeded (75 words over )')
  end
end
