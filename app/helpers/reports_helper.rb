# frozen_string_literal: true

module ReportsHelper
  def report_formats(report)
    (report.class.formats & Report.formats.keys)
  end

  def render_report_form(subreport)
    render partial: "#{subreport}_form",
           locals: { subreport: @report.manager.report_for(subreport, @report.parameters),
                     report_name: subreport.humanize }
  rescue ActionView::MissingTemplate
    render partial: 'report_form',
           locals: { subreport: @report.manager.report_for(subreport, @report.parameters),
                     report_name: subreport.humanize }
  end
end
