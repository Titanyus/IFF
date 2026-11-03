# All list/detail authorization goes through this one policy.
class CareCaseAccess
  def self.can_manage?(user)
    user&.in_group?("leitung") || user&.in_group?("verwaltung")
  end

  def self.can_trash?(user)
    user&.in_group?("leitung")
  end

  def self.scope(user, include_deleted: false)
    return CareCase.none unless user

    cases = if can_manage?(user)
      CareCase.all
    elsif user.in_group?("therapie")
      CareCase.joins(:case_assignments).where(case_assignments: { user_id: user.id }).distinct
    else
      CareCase.none
    end

    (include_deleted && can_trash?(user)) ? cases : cases.where(deleted_at: nil)
  end
end
