class ApplicationController < ActionController::Base
  before_action :require_login
  helper_method :current_user

  private

  def current_user
    @current_user ||= User.find_by(id: session[:user_id])
  end

  def require_login
    redirect_to new_session_path, alert: "Bitte anmelden." unless current_user
  end

  def require_manager
    head :forbidden unless CareCaseAccess.can_manage?(current_user)
  end

  def require_leader
    head :forbidden unless CareCaseAccess.can_trash?(current_user)
  end
end
