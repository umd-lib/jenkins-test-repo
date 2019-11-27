# frozen_string_literal: true

class LinksController < ApplicationController
  before_action :set_link, only: %i[show edit update destroy]
  after_action :verify_authorized

  rescue_from Pundit::NotAuthorizedError, with: :not_authorized

  def index
    authorize Link
  end

  def show
    authorize @link
  end

  def new
    authorize Link
    @link = Link.new
  end

  def edit
    authorize @link
  end

  def create
    authorize Link
    @link = Link.new(link_params)
    respond_to do |format|
      if @link.save(link_params)
        format.html { redirect_to @link, notice: "Link #{@link.text} was successfully created." }
      else
        format.html { render :new }
      end
    end
  end

  def update
    authorize @link
    respond_to do |format|
      if @link.update(link_params)
        format.html { redirect_to @link, notice: "Link #{@link.text} was successfully updated." }
      else
        format.html { render :edit }
      end
    end
  end

  def destroy
    authorize Link
    if @link.destroy
      flash[:notice] = "Link #{@link.text} was successfully deleted."
    else
      flash[:error] = "ERROR Deleting #{@link.text} #{@link.errors}"
    end
    respond_to do |format|
      format.html { redirect_to links_url }
    end
  end

  private

    def link_params
      params.require(:link).permit(:url, :text)
    end

    # Use callbacks to share common setup or constraints between actions.
    def set_link
      @link = Link.find(params[:id])
    end
end
