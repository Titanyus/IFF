class CareCase < ApplicationRecord
  STATUSES = %w[waiting active closed].freeze
  belongs_to :child
  has_many :case_assignments, dependent: :restrict_with_exception
  has_many :assigned_therapists, through: :case_assignments, source: :user
  has_many :audit_events, dependent: :restrict_with_exception
  validates :status, inclusion: { in: STATUSES }
  validates :requested_on, presence: true

  def deleted?
    deleted_at.present?
  end
end
