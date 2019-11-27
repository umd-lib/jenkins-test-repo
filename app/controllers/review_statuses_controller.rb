# frozen_string_literal: true

class ReviewStatusesController < ApplicationController
  before_action :set_review_status, only: %i[show edit update destroy]
  after_action :verify_authorized

  # GET /review_status
  def index
    authorize ReviewStatus
    @review_statuses = ReviewStatus.all.paginate(page: params[:page])
  end

  # GET /review_status/1
  def show
    authorize @review_status
  end

  # GET /review_status/new
  def new
    authorize ReviewStatus
    @review_status = ReviewStatus.new
  end

  # GET /review_status/1/edit
  def edit
    authorize @review_status
  end

  # POST /review_status
  def create
    authorize ReviewStatus
    @review_status = ReviewStatus.new(review_status_params)
    respond_to do |format|
      if @review_status.save
        format.html { redirect_to @review_status, notice: "Review Status #{@review_status.name} was successfully created." }
      else
        format.html { render :new }
      end
    end
  end

  # PATCH/PUT /review_status/1
  def update
    authorize @review_status
    respond_to do |format|
      if @review_status.update(review_status_params)
        format.html { redirect_to @review_status, notice: "Review Status #{@review_status.name} was successfully updated." }
      else
        format.html { render :edit }
      end
    end
  end

  # DELETE /review_status/1
  def destroy
    authorize ReviewStatus
    if @review_status.destroy
      flash[:notice] = "Review status #{@review_status.name} was successfully deleted."
    else
      flash[:error] = "ERROR Deleting #{@review_status.name} #{@review_status.errors}"
    end
    respond_to do |format|
      format.html { redirect_to review_statuses_url }
    end
  end

  private

    # Use callbacks to share common setup or constraints between actions.
    def set_review_status
      @review_status = ReviewStatus.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def review_status_params
      params.require(:review_status).permit(:name, :code, :color)
    end
end
