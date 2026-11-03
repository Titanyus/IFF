class CareCasesController < ApplicationController
  before_action :require_manager, only: [:new, :create, :activate, :close]
  before_action :require_leader, only: [:trash, :restore]

  def index
    @filter = params[:status].presence_in(%w[waiting active closed all trashed]) || "waiting"
    return head :forbidden if @filter == "trashed" && !CareCaseAccess.can_trash?(current_user)
    @cases = CareCaseAccess.scope(current_user, include_deleted: @filter == "trashed")
    @cases = @filter == "trashed" ? @cases.where.not(deleted_at: nil) : @cases.where(deleted_at: nil)
    @cases = @cases.where(status: @filter) if CareCase::STATUSES.include?(@filter)
    @cases = @cases.includes(:child).order(requested_on: :desc, id: :desc)
  end

  def show
    @care_case = visible_case
  end

  def new
    @guardians = Guardian.order(:full_name)
  end

  def create
    data = params.require(:care_case).permit(:first_name, :last_name, :requested_on, :guardian_id, :guardian_name)
    date = Date.iso8601(data[:requested_on].to_s)
    created = CareCase.transaction do
      child = Child.create!(first_name: data[:first_name].to_s.strip, last_name: data[:last_name].to_s.strip)
      guardian = if data[:guardian_id].present?
        Guardian.find(data[:guardian_id])
      else
        Guardian.create!(full_name: data[:guardian_name].to_s.strip)
      end
      ChildGuardian.create!(child: child, guardian: guardian, relation: "Sorgeberechtigt")
      care_case = CareCase.create!(child: child, requested_on: date, status: "waiting")
      AuditEvent.create!(care_case: care_case, actor: current_user, action: "created", to_status: "waiting")
      care_case
    end
    redirect_to care_case_path(created), notice: "Förderfall angelegt."
  rescue ArgumentError, ActiveRecord::RecordInvalid => e
    @guardians = Guardian.order(:full_name)
    flash.now[:alert] = "Anlage fehlgeschlagen: #{e.message}"
    render :new, status: :unprocessable_entity
  end

  def activate
    run_transition("active")
  end

  def close
    run_transition("closed")
  end

  def trash
    care_case = CareCase.where(deleted_at: nil).find(params[:id])
    CareCase.transaction do
      care_case.lock!
      care_case.update!(deleted_at: Time.current)
      AuditEvent.create!(care_case: care_case, actor: current_user, action: "trash")
    end
    redirect_to care_cases_path, notice: "In den Papierkorb verschoben.", status: :see_other
  end

  def restore
    care_case = CareCase.where.not(deleted_at: nil).find(params[:id])
    CareCase.transaction do
      care_case.lock!
      care_case.update!(deleted_at: nil)
      AuditEvent.create!(care_case: care_case, actor: current_user, action: "restore")
    end
    redirect_to care_cases_path(status: "trashed"), notice: "Wiederhergestellt.", status: :see_other
  end

  private

  def visible_case
    CareCaseAccess.scope(current_user, include_deleted: CareCaseAccess.can_trash?(current_user)).find(params[:id])
  end

  def run_transition(target)
    case_record = CareCaseAccess.scope(current_user).find(params[:id])
    CareCaseTransitions.call!(care_case: case_record, actor: current_user,
                              target: target, effective_on: params[:effective_on])
    redirect_to care_case_path(case_record), notice: "Status geändert.", status: :see_other
  rescue CareCaseTransitions::Invalid, ActiveRecord::RecordInvalid => e
    redirect_to care_case_path(params[:id]), alert: e.message, status: :see_other
  end
end
