class User < ApplicationRecord
  has_secure_password
  has_many :group_memberships, dependent: :destroy
  has_many :groups, through: :group_memberships
  has_many :case_assignments, dependent: :destroy
  has_many :assigned_care_cases, through: :case_assignments, source: :care_case
  validates :email, presence: true, uniqueness: { case_sensitive: false }

  def in_group?(slug)
    groups.exists?(slug: slug)
  end
end
