class Child < ApplicationRecord
  has_many :care_cases, dependent: :restrict_with_exception
  has_many :child_guardians, dependent: :restrict_with_exception
  has_many :guardians, through: :child_guardians
  validates :first_name, :last_name, presence: true, length: { maximum: 100 }

  def full_name
    "#{first_name} #{last_name}"
  end
end
