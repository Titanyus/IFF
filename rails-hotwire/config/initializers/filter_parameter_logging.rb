Rails.application.config.filter_parameters += [
  :password, :password_confirmation, :secret, :token,
  :first_name, :last_name, :guardian_name, :guardian_phone, :birth_date,
  :name, :full_name
]
