# frozen_string_literal: true

class ReportsController < ApplicationController
  before_action :set_report, only: %i[show edit update destroy download]
  after_action :verify_authorized, only: %i[index show create destroy download]

  # GET /reports
  # GET /reports.json
  def index
    authorize Report
    sort_order = params[:sort] || 'created_at desc'
    @reports = Report.order(sort_order).paginate(page: params[:page])
  end

  # GET /reports/1
  # GET /reports/1.json
  def show
    authorize Report
  end

  # GET /reports/new
  def new
    authorize Report
    @report = Report.new(creator: current_user)
  end

  # GET /reports/1/edit
  def edit
    redirect_to @report
  end

  # POST /reports
  # POST /reports.json
  def create # rubocop:disable Metrics/MethodLength
    authorize Report
    @report = Report.new(report_params)

    respond_to do |format|
      if @report.save
        ReportJob.perform_later @report
        format.html { redirect_to @report, notice: "Report for #{@report.description} was successfully created." }
        format.json { render :show, status: :created, location: @report }
      else
        format.html { render :new }
        format.json { render json: @report.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /reports/1
  # PATCH/PUT /reports/1.json
  def update
    render plain: 'Not Found', status: '404'
  end

  # DELETE /reports/1
  # DELETE /reports/1.json
  def destroy
    authorize Report
    respond_to do |format|
      if delete
        format.html { redirect_to reports_url, notice: "Report for #{@report.description} was successfully destroyed." }
        format.json { head :no_content }
      else
        format.html { redirect_to reports_url, flash: { error: @error_msg } }
        format.json { render json: [error], status: :unprocessable_entity }
      end
    end
  end

  def download
    authorize Report
    respond_to do |format|
      format.xlsx { send_data @report.output, filename: "#{@report.name}.xlsx", disposition: 'attachment' }
    end
  end

  private

    # Returns true if the current request type was deleted. If the request type
    # cannot be deleted due an ActiveRecord::DeleteRestrictionError, populates
    # @error_msg and returns false.
    def delete
      @report.destroy
      true
    rescue ActiveRecord::DeleteRestrictionError
      @error_msg = 'Request type cannot be removed as it is used by other records.'
      false
    end

    # Use callbacks to share common setup or constraints between actions.
    def set_report
      @report = Report.find(params[:id])
    end

    def report_params # rubocop:disable Metrics/MethodLength
      report_parameters_keys = params[:report][:parameters].try(:keys)
      if report_parameters_keys # rubocop:disable Style/SafeNavigation
        # The following modifies the report_parameters_keys map if any of the
        # keys are actually an array of values (such as might come back from
        # a bunch of checkboxes forming a group).
        report_parameters_keys.map! do |key|
          if params[:report][:parameters][key].is_a?(Array)
            [key.to_sym => []]
          else
            key
          end
        end
      end
      params.require(:report).permit(:name, :format, :user_id,
                                     parameters: report_parameters_keys)
    end
end
