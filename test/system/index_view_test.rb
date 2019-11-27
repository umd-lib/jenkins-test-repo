# frozen_string_literal: true

require 'application_system_test_case'
require 'fileutils'

class IndexViewTest < ApplicationSystemTestCase
  def setup
    login_admin
    FileUtils.mkdir(ApplicationSystemTestCase::DOWNLOAD_DIR) unless File.exist?(ApplicationSystemTestCase::DOWNLOAD_DIR)
    Dir.glob(File.join(ApplicationSystemTestCase::DOWNLOAD_DIR, '*')).each { |f| FileUtils.rm(f) }
  end

  test 'should keep page and sort when deleting' do
    click_link 'Labor and Assistance'
    click_link '2'
    click_link 'Submitted By'
    url = current_url

    row = all('tr').last
    name = row.find('td[headers="position_title"]').text
    accept_alert do
      row.find('a.delete').click
    end

    assert current_url == url
    assert page.has_content? name
    assert_not find('table').text.include? name
  end

  test 'should export from archive' do
    click_link 'Labor and Assistance'
    click_link 'View Archive'
    click_link 'Export'
    assert :success
    # we need to make sure the download finished.
    file = nil
    5.times do
      sleep 0.5
      file = Dir.glob(File.join(ApplicationSystemTestCase::DOWNLOAD_DIR, '*.xlsx')).first
      break if file
    end

    assert_not_nil file
    spreadsheet = Roo::Excelx.new(file)
    expected_row_count = ArchivedLaborRequest.count + 1 # include header row in count
    assert_equal expected_row_count, spreadsheet.last_row
  end

  test 'should keep to in archive when sorting' do
    click_link 'Labor and Assistance'
    click_link 'View Archive'
    click_link 'Submitted By'
    assert page.has_content? 'View Active'
    assert page.has_content? 'You are currently in the archive'
  end

  test 'should show My Requests page' do
    [LaborRequest, ContractorRequest, StaffRequest].each do |klass|
      record = klass.first
      record.user = users(:admin)
      record.save
    end
    click_link 'admin'
    click_link 'My Requests'
    assert :success
    ['Type', 'Position Title', 'Employee Type', 'Request Type', 'Employee Name', 'Contractor Name',
     'Annual Cost Or Base Pay', 'Department', 'Unit', 'Status', 'Submitted By']
      .shuffle.each_slice(3) do |links|
      links.each { |link| within('table') { click_link link } }
      assert :success
      click_link 'Reset Sorting'
    end
  end
end
